# neue-skills

Three agent skills that make an AI actually good at conversion work, by replacing taste
with gates.

Models do not write bad copy because they lack advice. They write bad copy because
nothing forces a number, a mechanism, or a commitment into a sentence. So these skills
ship **executable critics**: a copy linter and a page auditor that either exit `0` or
name the exact line to fix.

| Skill | Does | Gate |
|---|---|---|
| [`copywriter-superhero`](skills/copywriter-superhero/SKILL.md) | Conversion copy in a measured brand voice, three angles per task | `score_copy.py` — banned words and constructions, rhythm variance, specificity density, angle separation |
| [`conversion-architect`](skills/conversion-architect/SKILL.md) | Landing page assembly, CTA hierarchy, motion, accessibility, deploy | `audit_page.py` — section contract, one `h1`, CTA rules, a11y, metadata |
| [`json-exporter`](skills/json-exporter/SKILL.md) | Page spec + copy → deployable bundle | `export.py --validate-only` — spec shape, field counts, lengths |

The gates are why this works. On the same brief, generic model output scores **0/100** and
copy written through the skill scores **100/100** — and the brand's own published copy
passes its own gates at 86, which is how you know the gates measure the brand rather than
an opinion.

---

## Install

Skills are directories containing a `SKILL.md`. Install links them into your agent's
skills folder, so `git pull` updates them with no reinstall.

```bash
git clone https://github.com/neue-academy/neue-skills.git
cd neue-skills
./scripts/install.sh
```

| Flag | Installs into |
|---|---|
| *(none)* | `~/.cursor/skills/` **and** `~/.claude/skills/` |
| `--cursor` | `~/.cursor/skills/` only |
| `--claude` | `~/.claude/skills/` only |
| `--project` | `./.cursor/skills/` — shared with anyone who clones the repo |
| `--uninstall` | Removes the symlinks |

Then start a **new** agent session, since skills are discovered at session start.

### Cursor

`./scripts/install.sh --cursor`. The repo also ships `.cursorrules` and
`.cursor/rules/neue-skills.mdc`, so an agent working *inside* this repo is pointed at the
skills and the gates automatically, without any install step.

### Claude / Claude Code

`./scripts/install.sh --claude` links into `~/.claude/skills/`. Invoke by name:

> Use copywriter-superhero to write launch copy for the founding-member offer.

### Any other agent

There is nothing Cursor-specific in the skills. Point the agent at
`skills/<name>/SKILL.md` and let it run the scripts. Python 3.8+ standard library only,
no `pip install`.

### Verify

```bash
./scripts/selftest.sh     # 24 checks across all three skills
```

---

## The pipeline

```
brief
  → copywriter-superhero   →  draft.md    (score_copy.py must exit 0)
  → json-exporter          →  dist/       (spec validation must pass)
  → conversion-architect   →  audit       (audit_page.py must exit 0)
  → deploy_to_vercel.sh    →  live URL    (verified HTTP 200)
```

Every arrow is a gate, and the deploy script refuses to ship a page that fails the audit.

Run it end to end:

```bash
cp .env.example .env.local          # add your VERCEL_TOKEN

python3 skills/copywriter-superhero/scripts/score_copy.py draft.md

python3 skills/json-exporter/scripts/export.py \
  --spec skills/json-exporter/examples/neue-waitlist.json \
  --copy draft.md --angle logic --out dist/

./skills/conversion-architect/scripts/deploy_to_vercel.sh dist/ --project neue-landing
```

---

## How the copy gate works

**1. Voice is measured, not described.** `extract_voice_codex.py` reads real published
samples and emits `voice-codex.json`: sentence length and variance, punctuation habits,
jargon tolerance, metaphor frequency, capitalization, signature phrases, and the numeric
gates the linter enforces. "Bold but approachable" is unfalsifiable. "Mean sentence 13.6
words, relative variance 0.71, zero exclamation marks" is a target.

**2. Banned words always carry a replacement.** A bare ban list increases the banned word,
because the model has nowhere to go. Every row in
[`buzzword-replacement-table.md`](skills/copywriter-superhero/references/buzzword-replacement-table.md)
gives it a destination. That markdown file **is** the linter's rule source — editing the
table changes the gate, so the docs cannot drift from what is enforced.

**3. Constructions matter more than words.** Readers who cannot name a single banned word
still recognise `not just X, but Y`, `that's where X comes in`, and `designed to help you`.
Table B bans 32 of those shapes.

**4. Rhythm is the loudest tell.** Sentences of uniform length read as machine-written even
when every word is fine. The gate measures the coefficient of variation, which is
length-invariant, so an 80-word card and a 900-page landing page meet the same standard.

**5. Three angles are structural.** Every task returns a Logic, Pain, and Social Proof
angle, and the linter blocks any two that share more than half their content words. One
draft gives the reader nothing to choose between and you nothing to test.

**6. Brand terms are protected automatically.** A word on the banned list that the brand
uses twice or more in its own corpus is reclaimed as voice, not slop. A linter that fights
the brand gets overridden, and an overridden linter is worse than none.

---

## Repo layout

```
neue-skills/
├── README.md
├── AGENTS.md                     # cross-agent entry point
├── .cursorrules                  # points Cursor at skills/ every session
├── .cursor/rules/neue-skills.mdc # modern Cursor rule, always applied
├── .env.example                  # VERCEL_TOKEN goes in .env.local (gitignored)
├── requirements.txt              # stdlib only, documented
├── scripts/
│   ├── install.sh                # symlink skills into Cursor / Claude
│   └── selftest.sh               # 24-check regression gate
└── skills/
    ├── copywriter-superhero/
    │   ├── SKILL.md
    │   ├── references/
    │   │   ├── voice-codex.json          # build artefact — do not hand-edit
    │   │   ├── voice-codex-template.md
    │   │   ├── funnel-angle-recipes.md
    │   │   ├── buzzword-replacement-table.md
    │   │   └── voice-samples/            # verbatim published copy, the only codex input
    │   ├── scripts/
    │   │   ├── extract_voice_codex.py
    │   │   ├── score_copy.py             # the critic
    │   │   ├── rules.py
    │   │   └── textstats.py
    │   └── examples/
    │       ├── good-output-1.md          # 100/100
    │       ├── bad-output-1.md           # 0/100, same brief
    │       ├── brief-2-lesson-description.md
    │       ├── brief-3-launch-email.md
    │       └── gap-log.md                # every failure found, and its fix
    ├── conversion-architect/
    │   ├── SKILL.md
    │   ├── references/
    │   │   ├── conversion-anatomy.md
    │   │   ├── section-timing-constants.md
    │   │   └── accessibility-checklist.md
    │   ├── scripts/
    │   │   ├── audit_page.py
    │   │   └── deploy_to_vercel.sh
    │   └── examples/reference-page.html
    └── json-exporter/
        ├── SKILL.md
        ├── scripts/export.py
        └── examples/neue-waitlist.json
```

---

## Adapting this to another brand

1. Put 3–5 verbatim published samples in a new
   `skills/copywriter-superhero/references/voice-samples-<brand>/`, each with a
   `<!-- source: URL -->` line.
2. Generate the codex, then confirm the brand's own copy passes its own gates. If it does
   not, the corpus is too small — add samples rather than loosening gates.
3. Edit the buzzword table for anything specific to that brand's market.
4. Run `./scripts/selftest.sh`.

Full walkthrough:
[`voice-codex-template.md`](skills/copywriter-superhero/references/voice-codex-template.md).

## Contributing a fix

When output fails in a new way, classify it first:

- **Shape failure** (wrong form, missing element) → add an example pair answering the same
  brief, and log it in [`gap-log.md`](skills/copywriter-superhero/examples/gap-log.md).
- **Measurement failure** (a gate misfired) → fix the gate or the table, then re-verify
  every existing example with `./scripts/selftest.sh`.

Never close a gap by adding another paragraph of advice to a `SKILL.md`. Prose does not
change output shape; examples and gates do.

---

Skills by Revelium™ Studio for Neue Academy™.
