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

head "copywriter-superhero — rules, profiles and codex"

expect_exit 0 "buzzword table parses" python3 "$CW/scripts/rules.py"
expect_exit 0 "plain-language table parses" \
  python3 "$CW/scripts/rules.py" "$CW/references/plain-language-table.md"

# Every regime declared in profiles.json must be loadable and internally consistent.
expect_exit 0 "profiles.json declares five coherent regimes" python3 - "$CW" <<'PY'
import json, sys, pathlib
root = pathlib.Path(sys.argv[1])
profiles = json.loads((root / "references/profiles.json").read_text())["profiles"]
expected = {"microcopy", "short-form", "long-form", "editorial", "functional"}
assert set(profiles) == expected, "regimes drifted: %s" % sorted(profiles)
known = set(json.loads(
    (root / "references/profiles.json").read_text()
)["profiles"]["short-form"]["checks"])
for name, profile in profiles.items():
    for field in ("label", "discipline", "voice_governs", "checks", "gates"):
        assert field in profile, "%s is missing %s" % (name, field)
    assert set(profile["checks"]) == known, "%s declares a different check set" % name
    for check, severity in profile["checks"].items():
        assert severity in ("BLOCK", "WARN", "off"), "%s.%s = %r" % (name, check, severity)
    assert profile["gates"].get("min_score_to_pass"), "%s has no pass mark" % name
PY

python3 "$CW/scripts/extract_voice_codex.py" \
  --samples "$CW/references/voice-samples-neue-academy" \
  --out "$TMP/codex.json" >/dev/null 2>&1
if [[ -f "$TMP/codex.json" ]]; then
  if diff -q "$TMP/codex.json" "$CW/references/voice-codex-neue-academy.json" >/dev/null 2>&1; then
    ok "committed brand codex matches a fresh extraction"
  else
    bad "voice-codex-neue-academy.json is stale — regenerate and commit it"
  fi
else
  bad "voice codex extraction produced no output"
fi

# The default codex must keep the linter usable with zero brand input.
expect_exit 0 "default codex carries no brand voice" python3 - "$CW" <<'PY'
import json, sys, pathlib
codex = json.loads((pathlib.Path(sys.argv[1])
                    / "references/voice-codex-default.json").read_text())
assert codex["generated_from"]["total_words"] == 0, "default codex must not be extracted"
assert codex["protected_terms"] == [], "default codex must claim no brand terms"
assert codex["gates"] == {}, "default codex must not override regime gates"
PY

# The brand's own published copy must pass its own gates, or the gates are wrong.
cat "$CW"/references/voice-samples-neue-academy/*.md > "$TMP/corpus.md"
expect_exit 0 "brand corpus passes its own gates" \
  python3 "$CW/scripts/score_copy.py" "$TMP/corpus.md" --regime short-form --variants 1 \
    --codex "$CW/references/voice-codex-neue-academy.json"

head "copywriter-superhero — one passing example per regime"

expect_exit 0 "good-microcopy.md passes" \
  python3 "$CW/scripts/score_copy.py" "$CW/examples/good-microcopy.md" --regime microcopy
expect_exit 0 "good-long-form.md passes" \
  python3 "$CW/scripts/score_copy.py" "$CW/examples/good-long-form.md" --regime long-form
expect_exit 0 "good-editorial.md passes" \
  python3 "$CW/scripts/score_copy.py" "$CW/examples/good-editorial.md" --regime editorial
expect_exit 0 "good-functional.md passes" \
  python3 "$CW/scripts/score_copy.py" "$CW/examples/good-functional.md" --regime functional
for example in good-short-form brief-2-lesson-description brief-3-launch-email; do
  expect_exit 0 "$example.md passes" \
    python3 "$CW/scripts/score_copy.py" "$CW/examples/$example.md" --regime short-form
done

head "copywriter-superhero — the gates must bite"

expect_exit 1 "bad-short-form.md fails (generic AI copy)" \
  python3 "$CW/scripts/score_copy.py" "$CW/examples/bad-short-form.md" --regime short-form
expect_exit 1 "bad-microcopy.md fails (sales instincts in an interface)" \
  python3 "$CW/scripts/score_copy.py" "$CW/examples/bad-microcopy.md" --regime microcopy

# Reordering a long-form stage must fail, or the architecture contract is decoration.
python3 - "$CW/examples/good-long-form.md" "$TMP/reordered.md" <<'PY'
import sys
src, dst = sys.argv[1], sys.argv[2]
text = open(src, encoding="utf-8").read()
mech, proof, offer = (text.index(h) for h in ("## Mechanism", "## Proof", "## Offer"))
open(dst, "w", encoding="utf-8").write(
    text[:mech] + text[proof:offer] + text[mech:proof] + text[offer:]
)
PY
expect_exit 1 "long-form stage order is enforced" \
  python3 "$CW/scripts/score_copy.py" "$TMP/reordered.md" --regime long-form

# Microcopy judged as marketing, and marketing judged as microcopy, must both fail.
expect_exit 1 "routing matters: long-form copy fails the microcopy gates" \
  python3 "$CW/scripts/score_copy.py" "$CW/examples/good-long-form.md" --regime microcopy
expect_exit 1 "routing matters: microcopy fails the long-form architecture" \
  python3 "$CW/scripts/score_copy.py" "$CW/examples/good-microcopy.md" --regime long-form

# Auto-detection is a convenience, but it must not be wrong about its own examples.
expect_exit 0 "auto-detect routes every example correctly" python3 - "$CW" <<'PY'
import json, subprocess, sys, pathlib
root = pathlib.Path(sys.argv[1])
expected = {
    "good-microcopy.md": "microcopy",
    "good-short-form.md": "short-form",
    "good-long-form.md": "long-form",
    "good-editorial.md": "editorial",
    "good-functional.md": "functional",
}
for name, regime in expected.items():
    out = subprocess.run(
        [sys.executable, str(root / "scripts/score_copy.py"),
         str(root / "examples" / name), "--json"],
        capture_output=True, text=True,
    ).stdout
    got = json.loads(out)["regime_key"]
    assert got == regime, "%s auto-detected as %s, expected %s" % (name, got, regime)
PY

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
    --copy "$CW/examples/good-short-form.md" --angle logic --out "$TMP/dist"
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
      --copy "$CW/examples/good-short-form.md" --angle "$angle" --out "$TMP/dist-$RANDOM"
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
# A shell script committed without its exec bit is a script nobody can run.
while IFS= read -r script; do
  if [[ -x "$script" ]]; then
    ok "$script is executable"
  else
    bad "$script is not executable — chmod +x and git update-index --chmod=+x"
  fi
done < <(find scripts skills -name '*.sh' -type f | sort)

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
