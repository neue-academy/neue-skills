# neue-skills

Three agent skills that make an AI actually good at conversion work, by replacing taste
with gates.

Models do not write bad copy because they lack advice. They write bad copy because
nothing forces a number, a mechanism, or a commitment into a sentence. So these skills
ship **executable critics**: a copy linter and a page auditor that either exit `0` or
name the exact line to fix.

| Skill | Does | Gate |
|---|---|---|
| [`copywriter-superhero`](skills/copywriter-superhero/SKILL.md) | Any copy, routed by type: UX microcopy, marketing copy, long-form sales letters, books and scripts, terms and help articles | `score_copy.py --regime <name>` — regime-specific gates: banned words and constructions, rhythm variance, specificity density, reading grade, buried verbs, persuasion-architecture completeness, angle separation |
| [`conversion-architect`](skills/conversion-architect/SKILL.md) | Landing page assembly, CTA hierarchy, motion, accessibility, deploy | `audit_page.py` — section contract, one `h1`, CTA rules, a11y, metadata |
| [`json-exporter`](skills/json-exporter/SKILL.md) | Page spec + copy → deployable bundle | `export.py --validate-only` — spec shape, field counts, lengths |

The gates are why this works. On the same brief, generic model output scores **0/100** and
copy written through the skill scores **100/100** — and a brand's own published copy passes
its own gates at 86, which is how you know the gates measure the brand rather than an
opinion.

Copy work is **routed before it is written**. A 3-word button, a 90-word ad, a 1,300-word
sales letter, a chapter of a book, and a privacy policy are graded against five different
rulebooks, because they are five different jobs. Brand voice is an optional last filter, so
the skill produces structurally correct copy with zero brand input and sharpens when a voice
codex exists.

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

python3 skills/copywriter-superhero/scripts/score_copy.py draft.md --regime short-form

python3 skills/json-exporter/scripts/export.py \
  --spec skills/json-exporter/examples/neue-waitlist.json \
  --copy draft.md --angle logic --out dist/

./skills/conversion-architect/scripts/deploy_to_vercel.sh dist/ --project neue-landing
```

---

## How the copy gate works

**1. The job is routed before it is written.** A button label, an ad, a sales letter, a
chapter, and a privacy policy share almost no standards, so the skill classifies the work
into one of five regimes first — microcopy, short-form, long-form, editorial, functional —
and loads that regime's rulebook. Hedges are banned in microcopy and load-bearing in legal.
Adverbs are a warning in ads and a block in prose. A missing CTA is a defect in a sales
letter and correct in a novel. One rulebook for all five is why default AI copy feels flat
whatever you ask it for.

Which checks run, and at what severity, is declared per regime in
[`profiles.json`](skills/copywriter-superhero/references/profiles.json). Routing is proven,
not asserted: the selftest requires that long-form copy **fails** the microcopy gates and
microcopy **fails** the long-form architecture.

**2. Voice is measured, not described — and it is optional.** With no brand samples the
linter uses plain-language defaults, so the skill is never blocked on onboarding a voice.
When samples exist, `extract_voice_codex.py` reads them and emits a codex: sentence length
and variance, punctuation habits, jargon tolerance, metaphor frequency, capitalization,
signature phrases, and numeric gates. "Bold but approachable" is unfalsifiable. "Mean
sentence 13.6 words, relative variance 0.71, zero exclamation marks" is a target.

Voice is applied **last**, and only where it belongs: it governs style gates in short-form,
long-form and editorial work, and never overrides clarity law on a button or in a contract.

**3. Banned words always carry a replacement.** A bare ban list increases the banned word,
because the model has nowhere to go. Every row in
[`buzzword-replacement-table.md`](skills/copywriter-superhero/references/buzzword-replacement-table.md)
gives it a destination. That markdown file **is** the linter's rule source — editing the
table changes the gate, so the docs cannot drift from what is enforced.

**4. Constructions matter more than words.** Readers who cannot name a single banned word
still recognise `not just X, but Y`, `that's where X comes in`, and `designed to help you`.
Table B bans 32 of those shapes.

**5. Rhythm is the loudest tell.** Sentences of uniform length read as machine-written even
when every word is fine. The gate measures the coefficient of variation, which is
length-invariant, so an 80-word card and a 5,000-word sales letter meet the same standard.

**6. Three angles are structural.** Every short-form task returns a Logic, Pain, and Social Proof
angle, and the linter blocks any two that share more than half their content words. One
draft gives the reader nothing to choose between and you nothing to test.

**7. Brand terms are protected automatically.** A word on the banned list that the brand
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
│   └── selftest.sh               # 38-check regression gate
└── skills/
    ├── copywriter-superhero/
    │   ├── SKILL.md
    │   ├── references/
    │   │   ├── profiles.json             # the five regimes: which gate applies where
    │   │   ├── frameworks.md             # AIDA/PAS/BAB/FAB/4Ps/PASTOR/SB7 + awareness
    │   │   ├── microcopy-rules.md        # buttons, errors, empty states
    │   │   ├── long-form-architecture.md # ten stages, and the long-vs-short rule
    │   │   ├── editorial-and-narrative.md  # books, scripts, essays, speeches
    │   │   ├── functional-and-legal.md   # terms, policies, help, release notes
    │   │   ├── buzzword-replacement-table.md
    │   │   ├── plain-language-table.md   # loaded on top, for functional copy
    │   │   ├── funnel-angle-recipes.md
    │   │   ├── voice-codex-template.md
    │   │   ├── voice-codex-default.json  # brand-agnostic fallback
    │   │   ├── voice-codex-neue-academy.json  # build artefact — do not hand-edit
    │   │   └── voice-samples-neue-academy/    # verbatim published copy, the codex input
    │   ├── scripts/
    │   │   ├── extract_voice_codex.py
    │   │   ├── score_copy.py             # the critic
    │   │   ├── rules.py
    │   │   └── textstats.py
    │   └── examples/                     # one passing example per regime
    │       ├── good-microcopy.md
    │       ├── bad-microcopy.md          # the same strings, written badly
    │       ├── good-short-form.md
    │       ├── bad-short-form.md         # same brief as good-short-form
    │       ├── good-long-form.md
    │       ├── good-editorial.md
    │       ├── good-functional.md
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
