#!/usr/bin/env bash
#
# Install the skills in this repo into your agent's skills directory by symlink, so
# `git pull` updates them with no reinstall.
#
#   ./scripts/install.sh              # both Cursor and Claude
#   ./scripts/install.sh --cursor     # Cursor only
#   ./scripts/install.sh --claude     # Claude only
#   ./scripts/install.sh --project    # into ./.cursor/skills (shared via the repo)
#   ./scripts/install.sh --uninstall
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_SRC="${REPO_ROOT}/skills"

DO_CURSOR=1
DO_CLAUDE=1
PROJECT_LOCAL=0
UNINSTALL=0

say()  { printf '\033[1m›\033[0m %s\n' "$1"; }
die()  { printf 'install: %s\n' "$1" >&2; exit 1; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cursor)    DO_CLAUDE=0; shift ;;
    --claude)    DO_CURSOR=0; shift ;;
    --project)   PROJECT_LOCAL=1; DO_CLAUDE=0; shift ;;
    --uninstall) UNINSTALL=1; shift ;;
    -h|--help)   sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) die "unknown flag: $1" ;;
  esac
done

[[ -d "$SKILLS_SRC" ]] || die "no skills/ directory at $SKILLS_SRC"

TARGETS=()
[[ "$PROJECT_LOCAL" -eq 1 ]] && TARGETS+=("${REPO_ROOT}/.cursor/skills")
if [[ "$PROJECT_LOCAL" -eq 0 ]]; then
  [[ "$DO_CURSOR" -eq 1 ]] && TARGETS+=("${HOME}/.cursor/skills")
  [[ "$DO_CLAUDE" -eq 1 ]] && TARGETS+=("${HOME}/.claude/skills")
fi

for target in "${TARGETS[@]}"; do
  mkdir -p "$target"
  for skill_dir in "$SKILLS_SRC"/*/; do
    name="$(basename "$skill_dir")"
    link="${target}/${name}"

    if [[ ! -f "${skill_dir}SKILL.md" && -f "${skill_dir}IMPLEMENTATION-PLAN.md" ]]; then
      say "skipping $name until SKILL.md exists"
      continue
    fi

    if [[ "$UNINSTALL" -eq 1 ]]; then
      if [[ -L "$link" ]]; then
        rm "$link"; say "removed ${link/#$HOME/~}"
      fi
      continue
    fi

    if [[ -L "$link" ]]; then
      rm "$link"
    elif [[ -e "$link" ]]; then
      die "$link exists and is not a symlink. Move it aside, then re-run."
    fi
    ln -s "${skill_dir%/}" "$link"
    say "linked ${link/#$HOME/~} → skills/$name"
  done
done

[[ "$UNINSTALL" -eq 1 ]] && { say "uninstalled"; exit 0; }

say "verifying"
FAIL=0
for skill_dir in "$SKILLS_SRC"/*/; do
  name="$(basename "$skill_dir")"
  if [[ ! -f "${skill_dir}SKILL.md" ]]; then
    if [[ -f "${skill_dir}IMPLEMENTATION-PLAN.md" ]]; then
      say "skipping $name until SKILL.md exists"
      continue
    fi
    printf '  missing SKILL.md in %s\n' "$name" >&2; FAIL=1; continue
  fi
  if ! head -5 "${skill_dir}SKILL.md" | grep -q "^name: ${name}$"; then
    printf '  %s: frontmatter name does not match the directory name\n' "$name" >&2
    FAIL=1; continue
  fi
  printf '  ok  %s\n' "$name"
done
[[ "$FAIL" -eq 0 ]] || die "one or more skills are malformed"

cat <<'EOF'

Installed. Start a new agent session, then try:

  "Use copywriter-superhero to write launch copy for <offer>"
  "Use conversion-architect to build and deploy a landing page for it"

Run ./scripts/selftest.sh to confirm every gate still passes.
EOF
