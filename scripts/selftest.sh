#!/usr/bin/env bash
#
# Regression gate for every skill in this repo.
#
# Run this after changing any gate, table, script, or example. A change that makes an
# existing example flip verdict is a regression, not an improvement.
#
#   ./scripts/selftest.sh
#
set -uo pipefail

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

CW="skills/copywriter-superhero"
CA="skills/conversion-architect"
JE="skills/json-exporter"
TMP="$(mktemp -d "${TMPDIR:-/tmp}/neue-selftest.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

PASS=0
FAIL=0

ok()   { printf '  \033[32mok\033[0m    %s\n' "$1"; PASS=$((PASS+1)); }
bad()  { printf '  \033[31mFAIL\033[0m  %s\n' "$1"; FAIL=$((FAIL+1)); }
head() { printf '\n\033[1m%s\033[0m\n' "$1"; }

# expect_exit <expected> <label> <command...>
expect_exit() {
  local expected="$1" label="$2"; shift 2
  local out; out="$("$@" 2>&1)"; local code=$?
  if [[ "$code" == "$expected" ]]; then
    ok "$label"
  else
    bad "$label (exit $code, expected $expected)"
    printf '%s\n' "$out" | sed 's/^/        /' | tail -12
  fi
}

head "copywriter-superhero — rules and codex"

expect_exit 0 "buzzword table parses" python3 "$CW/scripts/rules.py"

python3 "$CW/scripts/extract_voice_codex.py" \
  --samples "$CW/references/voice-samples" \
  --out "$TMP/codex.json" >/dev/null 2>&1
if [[ -f "$TMP/codex.json" ]]; then
  if diff -q "$TMP/codex.json" "$CW/references/voice-codex.json" >/dev/null 2>&1; then
    ok "committed voice-codex.json matches a fresh extraction"
  else
    bad "voice-codex.json is stale — regenerate and commit it"
  fi
else
  bad "voice codex extraction produced no output"
fi

# The brand's own published copy must pass its own gates, or the gates are wrong.
cat "$CW"/references/voice-samples/*.md > "$TMP/corpus.md"
expect_exit 0 "brand corpus passes its own gates" \
  python3 "$CW/scripts/score_copy.py" "$TMP/corpus.md" --mode single

head "copywriter-superhero — examples"

expect_exit 1 "bad-output-1.md fails (generic AI copy)" \
  python3 "$CW/scripts/score_copy.py" "$CW/examples/bad-output-1.md"
for example in good-output-1 brief-2-lesson-description brief-3-launch-email; do
  expect_exit 0 "$example.md passes" \
    python3 "$CW/scripts/score_copy.py" "$CW/examples/$example.md"
done

head "conversion-architect — page audit"

expect_exit 0 "reference-page.html passes the audit" \
  python3 "$CA/scripts/audit_page.py" "$CA/examples/reference-page.html"

# Negative test: an auditor that passes everything is worse than none.
python3 - "$CA/examples/reference-page.html" "$TMP/broken.html" <<'PY'
import sys
src, dst = sys.argv[1], sys.argv[2]
html = open(src, encoding="utf-8").read()
html = html.replace('<h2>The three things people ask first</h2>',
                    '<h1>The three things people ask first</h1>')
html = html.replace('data-section="objections"', 'data-section="extras"')
html = html.replace('<meta name="viewport" content="width=device-width, initial-scale=1">', '')
html = html.replace('<input id="email" name="email"', '<input name="email"')
open(dst, "w", encoding="utf-8").write(html)
PY
expect_exit 1 "audit catches injected violations" \
  python3 "$CA/scripts/audit_page.py" "$TMP/broken.html"

expect_exit 0 "deploy_to_vercel.sh is syntactically valid" \
  bash -n "$CA/scripts/deploy_to_vercel.sh"
if [[ -x "$CA/scripts/deploy_to_vercel.sh" ]]; then
  ok "deploy_to_vercel.sh is executable"
else
  bad "deploy_to_vercel.sh is not executable — run chmod +x"
fi

head "json-exporter — spec and pipeline"

expect_exit 0 "example spec validates" \
  python3 "$JE/scripts/export.py" --spec "$JE/examples/neue-waitlist.json" --validate-only

# A bad spec must fail before writing anything.
python3 - "$JE/examples/neue-waitlist.json" "$TMP/bad-spec.json" <<'PY'
import json, sys
spec = json.load(open(sys.argv[1], encoding="utf-8"))
spec["objections"]["items"] = spec["objections"]["items"][:1]
spec["meta"]["description"] = "too short"
json.dump(spec, open(sys.argv[2], "w", encoding="utf-8"))
PY
expect_exit 2 "invalid spec is rejected" \
  python3 "$JE/scripts/export.py" --spec "$TMP/bad-spec.json" --validate-only

expect_exit 0 "bundle builds from spec + copy" \
  python3 "$JE/scripts/export.py" --spec "$JE/examples/neue-waitlist.json" \
    --copy "$CW/examples/good-output-1.md" --angle logic --out "$TMP/dist"
expect_exit 0 "exported page passes the audit" \
  python3 "$CA/scripts/audit_page.py" "$TMP/dist/index.html"
for artefact in index.html og.svg manifest.json; do
  if [[ -s "$TMP/dist/$artefact" ]]; then
    ok "bundle contains $artefact"
  else
    bad "bundle is missing $artefact"
  fi
done

# Every angle must be buildable, not only the default.
for angle in pain "social proof"; do
  expect_exit 0 "builds the \"$angle\" angle" \
    python3 "$JE/scripts/export.py" --spec "$JE/examples/neue-waitlist.json" \
      --copy "$CW/examples/good-output-1.md" --angle "$angle" --out "$TMP/dist-$RANDOM"
done

head "hygiene"

# Only files git would actually commit. Scanning the working tree would flag the
# gitignored .env.local, which is exactly where the token is supposed to live.
LEAKED=""
if git rev-parse --git-dir >/dev/null 2>&1; then
  while IFS= read -r tracked; do
    [[ -f "$tracked" ]] || continue
    if grep -qIE 'vcp_[A-Za-z0-9]{20,}' "$tracked" 2>/dev/null; then
      LEAKED="$LEAKED $tracked"
    fi
  done < <(git ls-files --cached --others --exclude-standard)
fi
if [[ -n "$LEAKED" ]]; then
  bad "a Vercel-shaped token appears in committable file(s):$LEAKED"
else
  ok "no Vercel token in any committable file"
fi
for skill in "$CW" "$CA" "$JE"; do
  lines=$(grep -c '' "$skill/SKILL.md")
  if [[ "$lines" -le 500 ]]; then
    ok "$(basename "$skill")/SKILL.md is $lines lines (budget 500)"
  else
    bad "$(basename "$skill")/SKILL.md is $lines lines, over the 500-line budget"
  fi
done

printf '\n\033[1m%d passed, %d failed\033[0m\n' "$PASS" "$FAIL"
[[ "$FAIL" -eq 0 ]] || exit 1
