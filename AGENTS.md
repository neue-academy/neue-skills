# AGENTS.md

Entry point for any coding agent working in this repo.

## What is here

Three skills in `skills/`, each a directory with a `SKILL.md`. Read the relevant one in
full before working in its area.

| Task | Skill |
|---|---|
| Marketing copy of any kind — headlines, landing sections, emails, ads, social, taglines | `skills/copywriter-superhero/SKILL.md` |
| Landing page structure, CTA hierarchy, layout, motion, accessibility, deploy | `skills/conversion-architect/SKILL.md` |
| Exporting a page spec into deployable artefacts | `skills/json-exporter/SKILL.md` |

## Rules

1. **Copy must pass the linter before a human sees it.**
   `python3 skills/copywriter-superhero/scripts/score_copy.py draft.md` → exit 0.
2. **Pages must pass the audit before deploy.**
   `python3 skills/conversion-architect/scripts/audit_page.py page.html` → exit 0.
3. **Load the voice codex before writing copy.**
   `skills/copywriter-superhero/references/voice-codex.json`. Never invent a voice from
   adjectives. Never hand-edit the codex — it is regenerated from `references/voice-samples/`.
4. **Respect boundaries.** Copy is written only by `copywriter-superhero`. Structure
   belongs only to `conversion-architect`. Export belongs only to `json-exporter`.
5. **Fix the copy, not the gate.** If a gate blocks genuinely good work, change the input
   — add a real voice sample, or fix the replacement table — then re-run the selftest.
6. **Never commit a secret.** `VERCEL_TOKEN` comes from the environment or `.env.local`.

## Commands

```bash
./scripts/selftest.sh        # 24 checks, run after any change to a gate or example
./scripts/install.sh         # link skills into ~/.cursor/skills and ~/.claude/skills
```

## Code conventions

- Python 3.8+ **standard library only**. A skill that needs `pip install` will not get run.
- Scripts print a finding, a line number, and a specific fix. Never just "invalid".
- Exit codes are the interface: `0` pass, `1` fail, `2` usage or config error.
- The markdown reference files are the rule source. `score_copy.py` parses
  `buzzword-replacement-table.md` directly, so the docs cannot drift from the enforced rules.

## Do not

- Do not add a banned word to the protected list to make a draft pass. That inverts the tool.
- Do not weaken a gate to pass a bad draft. Verify against every existing example first.
- Do not write copy inside `conversion-architect`, or page markup inside `copywriter-superhero`.
