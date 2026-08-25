# AGENTS.md

Entry point for any coding agent working in this repo.

## What is here

Three skills in `skills/`, each a directory with a `SKILL.md`. Read the relevant one in
full before working in its area.

| Task | Skill |
|---|---|
| Any copy at all — UX microcopy, marketing copy, sales letters, books, scripts, newsletters, terms, help articles | `skills/copywriter-superhero/SKILL.md` |
| Landing page structure, CTA hierarchy, layout, motion, accessibility, deploy | `skills/conversion-architect/SKILL.md` |
| Exporting a page spec into deployable artefacts | `skills/json-exporter/SKILL.md` |

## Rules

1. **Triage before drafting.** State the regime (microcopy, short-form, long-form,
   editorial, functional), the reader's awareness level, and the traffic temperature, then
   open that regime's rulebook. Routing by habit is the failure this repo exists to stop.
2. **Copy must pass the linter before a human sees it.**
   `python3 skills/copywriter-superhero/scripts/score_copy.py draft.md --regime <regime>`
   → exit 0. Always pass `--regime`; omitting it auto-detects and prints its guess.
3. **Pages must pass the audit before deploy.**
   `python3 skills/conversion-architect/scripts/audit_page.py page.html` → exit 0.
4. **Brand voice is optional and comes last.** With no `--codex` the linter uses
   plain-language defaults. When brand samples exist, extract a codex from **verbatim
   published copy** and apply it as a final filter. Never hand-edit a codex, and never
   write the samples yourself — that measures the model, not the brand.
5. **Respect boundaries.** Copy is written only by `copywriter-superhero`. Structure
   belongs only to `conversion-architect`. Export belongs only to `json-exporter`.
6. **Fix the copy, not the gate.** If a gate blocks genuinely good work, change the input
   — add a real voice sample, or fix the replacement table — then re-run the selftest.
7. **Never commit a secret.** `VERCEL_TOKEN` comes from the environment or `.env.local`.

## Commands

```bash
./scripts/selftest.sh        # 38 checks, run after any change to a gate or example
./scripts/install.sh         # link skills into ~/.cursor/skills and ~/.claude/skills
```

## Code conventions

- Python 3.8+ **standard library only**. A skill that needs `pip install` will not get run.
- Scripts print a finding, a line number, and a specific fix. Never just "invalid".
- Exit codes are the interface: `0` pass, `1` fail, `2` usage or config error.
- The markdown reference files are the rule source. `score_copy.py` parses
  `buzzword-replacement-table.md` directly, so the docs cannot drift from the enforced rules.
- Thresholds live in `references/profiles.json`, one profile per regime. Add a check by
  declaring it in every profile, then implementing it once in `score_copy.py`.

## Do not

- Do not add a banned word to the protected list to make a draft pass. That inverts the tool.
- Do not weaken a gate to pass a bad draft. Verify against every existing example first.
- Do not write copy inside `conversion-architect`, or page markup inside `copywriter-superhero`.
