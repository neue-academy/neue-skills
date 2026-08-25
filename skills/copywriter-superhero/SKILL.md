---
name: copywriter-superhero
description: Use when writing, rewriting, punching up, shortening, or reviewing any copy a reader will see — UX microcopy (buttons, errors, empty states, tooltips), marketing copy (headlines, ads, emails, product descriptions), long-form sales copy (landing pages, VSLs, sales letters), editorial work (books, chapters, scripts, essays, newsletters), or functional documents (terms, privacy policies, help articles, release notes). Routes by copy type and reader awareness, then lints until the quality gate exits 0. Brand voice is optional and applied last. Use whenever copy sounds like AI and needs to stop.
---

# Copywriter Superhero

Most AI copy fails for one reason: the model optimises for **coverage** instead of
**commitment**. It hedges every claim, names no numbers, keeps every sentence the same
length, and describes the category instead of the thing.

The second reason is subtler and more expensive: **it applies one rulebook to every job.**
A button label, a 5,000-word sales letter, a chapter of a book, and a privacy policy share
almost no standards. Copy that borrows sales instincts for a button is unusable. Copy that
borrows UX brevity for a cold-traffic sales page cannot close.

So this skill routes first and writes second.

## The loop — never skip a step

```
Task Progress:
- [ ] 1. Triage: state the regime, awareness level, and traffic temperature out loud
- [ ] 2. Route: open that regime's rulebook and pick the framework
- [ ] 3. Brief: fill every slot that applies. No blanks
- [ ] 4. Draft in the structure the regime requires
- [ ] 5. Lint with --regime. Fix. Re-run. Repeat until exit 0
- [ ] 6. Voice pass — only if brand samples exist. Then lint again
- [ ] 7. Hand over with the scorecard and invite steering
```

Do not show the user a draft that has not exited 0. A failing draft wastes their review,
and the linter finds in 200ms what a human finds in ten minutes.

---

## Step 1 — Triage before anything else

Answer these three questions in the open. Routing done by habit cannot be checked;
routing decided in writing can.

**a) What TYPE of copy is this?** One of five regimes (table in Step 2).

**b) What is the reader's awareness level?** Unaware, problem-aware, solution-aware,
product-aware, or most aware. This single variable decides the framework, and getting it
wrong is the most expensive error in copywriting — explaining the problem to a ready buyer
insults them, and leading with price to an unaware reader loses them in one line.

**c) Is the traffic cold, warm, or hot?** Cold needs the full build. Hot needs the offer
and nothing else.

Then paste this block at the top of the deliverable and fill it:

```markdown
### Triage
- **Regime:** short-form marketing
- **Deliverable:** hero section, 3 angles, 90 words each
- **Awareness:** problem-aware — they feel the rebuild cost, don't know a fix exists
- **Traffic:** cold
- **Framework:** PAS — problem-aware audience, fast conversion
- **Voice source:** none supplied → plain-language default
- **Lint command:** score_copy.py draft.md --regime short-form
```

The linter checks that `Regime:` and `Awareness:` are present. Definitions and the full
awareness matrix: [references/frameworks.md](references/frameworks.md).

---

## Step 2 — Route to the rulebook

| Regime | Examples | Length | Governing discipline | Rulebook |
|---|---|---|---|---|
| **microcopy** | Buttons, error messages, empty states, tooltips, labels, confirmations | 1–15 words | NN/g 3 C's: clarity, then concision, then character | [microcopy-rules.md](references/microcopy-rules.md) |
| **short-form** | Ads, headlines, hero sections, social posts, short emails, product descriptions | 15–300 words | Direct response: AIDA, PAS, BAB, FAB, matched to awareness | [frameworks.md](references/frameworks.md) |
| **long-form** | Sales pages, VSL scripts, long email sequences, webinar scripts | 1,500–12,000+ | Ten-stage persuasion architecture, in fixed order | [long-form-architecture.md](references/long-form-architecture.md) |
| **editorial** | Books, chapters, screenplays, scripts, essays, newsletters, speeches, docs prose | 200–100,000+ | Information reveal and scene structure. No CTA to reach | [editorial-and-narrative.md](references/editorial-and-narrative.md) |
| **functional** | Terms, privacy policies, contracts, transactional email, help articles, release notes | any | Plain-language law: precision, then navigability, zero persuasion | [functional-and-legal.md](references/functional-and-legal.md) |

**Open the rulebook. Do not write from memory.** Each one carries constraints that
contradict the others on purpose — hedges are banned in microcopy and load-bearing in
legal; adverbs are a WARN in ads and a BLOCK in prose; a missing CTA is a defect in
long-form and correct in editorial.

**When a job spans regimes, split it.** A landing page is a short-form hero plus microcopy
plus functional footer text. Write and lint each part under its own regime, then assemble.
Never average the rules together.

Which checks run, and at what severity, is declared per regime in
[references/profiles.json](references/profiles.json). That file is the source of truth for
every threshold in this skill.

---

## Step 3 — Fill the brief

Complete every slot that applies **before drafting**. A blank slot is the single most
common cause of generic copy, so it gets a required field, not a reminder.

```markdown
### Brief
- **Role framing:** who is speaking, and what have they personally done that earns the claim
- **Reader:** one person. Job, stage, budget, what they tried last and why it failed
- **Offer / subject specifics:** exact deliverables, counts, price, dates, access terms
- **Proof points:** numbers, named customers, screenshots, guarantees — with sources
- **Guardrails:** claims that are legally or factually off-limits
- **Channel spec:** medium, placement, character limits, reading context
- **Output variants:** how many angles or options, plus required lengths
- **Scoring rubric:** what "good" means for this specific task
```

For **editorial**, replace *Offer specifics* with premise, POV, tense, and the reader's
prior knowledge. For **functional**, replace *Proof points* with jurisdiction, binding
status, and who signs off.

Rules for filling it:

- **One reader.** Two readers in one brief produces copy that speaks to neither. If the
  user gives you two, pick the one closest to buying and say which one you picked.
- **If a slot is genuinely unknown, write `UNKNOWN — assumption: <x>`** and carry on.
  Never silently invent proof. Invented numbers are the one unrecoverable failure here.
- **Ask at most two questions.** Draft against stated assumptions instead of stalling. A
  concrete draft with visible assumptions gets corrected faster than a question does.

---

## Step 4 — Draft in the required structure

### microcopy — one labelled item per string

```markdown
### Button — save draft
Save draft

### Error — email missing @
That email address is missing an "@". Add it and try again.
```

The kind before the dash drives the rules: buttons get 4 words and a verb first, errors
get the `[what went wrong] + [why] + [how to fix it]` formula, and blame is banned
outright. The linter checks each item against its own kind.

### short-form — three angles, always

Not three rewordings. Three different arguments for the same decision. The linter blocks
any two angles sharing more than half their content words.

| Angle | Leads with | Proof it must carry |
|---|---|---|
| **Logic** | The arithmetic. Time, money, or output, counted | A number the reader can verify |
| **Pain** | The cost of doing nothing, named concretely | The specific friction, in the reader's words |
| **Social Proof** | Someone like the reader who already did it | An attributable result or quote |

```markdown
## Angle 1 — Logic
### Headline
### Subhead
### Body
### CTA
```

Repeat for Pain and Social Proof. Match the headings exactly; the linter parses them.
Recipes and openers: [references/funnel-angle-recipes.md](references/funnel-angle-recipes.md).

For a genuine single-variant job, pass `--variants 1` and say why in the handover.

### long-form — ten stages, in order

`## Headline` → `## Hook` → `## Problem` → `## Credibility` → `## Mechanism` →
`## Proof` → `## Offer` → `## Guarantee` → `## Close` → `## P.S.`

A missing or out-of-order stage is a BLOCK. Each stage answers a question the reader is
already asking silently; skip one and you lose them exactly there. What belongs in each,
plus the long-versus-short decision rule:
[references/long-form-architecture.md](references/long-form-architecture.md).

### editorial — structure by information reveal

No fixed heading contract, because a chapter and a screenplay do not share one. Every
unit either opens a question or answers one. Rhythm variance and repeated openers are
BLOCK findings here, and adverbs are BLOCK.

### functional — rule first, exceptions second

Numbered sections with descriptive titles. Second person, present tense, active voice,
one obligation per sentence. Real deadlines, never standards of effort. This regime
**drafts but never advises** — a lawyer signs off, and a lawyer's wording always wins.

---

## The craft rules the linter cannot check

The linter catches slop. These make copy good. They hold in every regime unless a rulebook
overrides them.

**1. Write on the fourth rung of the specificity ladder.**
`creative tools` → `design software` → `Figma and Blender` → `Figma, Blender and After
Effects, in one 40-minute build`. Rung four, always. If a photographer could not
photograph your noun, replace the noun.

**2. Every benefit needs a mechanism.**
Claim, then `because` + the thing that makes it true. "You ship in a weekend" is a wish.
"You ship in a weekend because every lesson hands you the production repo, not a blank
file" is an argument.

**3. One claim per sentence.**
Two claims joined by "and" means the reader remembers neither. Split them. This is also
the cheapest way to earn rhythm variance.

**4. Open on the reader's situation, not your product.**
The first sentence you write is almost always throat-clearing. Delete it and start at
sentence two. Do this on every draft — it works nearly every time.

**5. Long build, short landing.**
A 24-word sentence that sets up a 4-word sentence lands. Four 14-word sentences in a row
read like a model. The `flat-rhythm` gate exists because this is the loudest tell.

**6. Proof discipline.** Three kinds, in descending strength: *measured* (a number with a
source), *demonstrated* (a screenshot, a repo, a before/after), *asserted* (a quote).
Never assert what you could measure. Never measure what you cannot source.

**7. CTAs are verb + object, optionally + friction reducer.**
"Claim the founding rate" beats "Ready to get started?". A question CTA asks permission;
an imperative assumes the sale. Add the friction reducer only if it is true.

**8. Cut the last sentence of every paragraph** if it restates the paragraph. Models
explain the joke. Stop at the fact and let it sit.

**9. Structure is felt, never announced.** Never write "Now let me agitate this problem".
Name the framework in the triage block, then never again.

**10. Read it aloud.** Any sentence you cannot say in one breath gets split. Any sentence
that makes you wince gets deleted, not softened.

---

## Step 5 — Lint until it passes

```bash
python3 skills/copywriter-superhero/scripts/score_copy.py draft.md --regime short-form
```

The linter loads the regime profile, the replacement tables, and — if supplied — a brand
codex, then reports every finding with a line number and a specific fix.

- **BLOCK** findings must all be fixed. No exceptions, no negotiating.
- **WARN** findings must be fixed or justified in one line to the user.
- Exit `0` means it passes. Exit `1` means keep working.

| Flag | Use |
|---|---|
| `--regime <name>` | Always pass it. Omitting it auto-detects and prints its guess |
| `--variants 1` | Single-variant deliverable; disables the three-angle requirement |
| `--codex <path>` | Apply a brand voice. Omit for plain-language defaults |
| `--json` | Machine-readable output |
| `-` | Read the draft from stdin |

**When a fix fights a gate, fix the copy, never the gate.** Thresholds live in
`profiles.json` and represent the discipline, not a preference. The one legitimate
exception is a brand that genuinely writes a flagged word repeatedly — that is handled in
Step 6, by evidence, not by editing the gate.

**Never add a banned word to the protected list to make a draft pass.** That inverts the
tool.

---

## Step 6 — Voice pass (optional, and last)

Structure, argument, and sentences are locked before voice is applied. Applying voice
earlier produces on-brand copy with no spine.

**If the user supplied no brand samples**, stop here. The default is clear, direct,
plain-language prose per NN/g's clarity-first principle, and it is a good default — the
draft is already correct.

**If brand samples exist**, extract a codex from verbatim published copy and re-lint:

```bash
python3 skills/copywriter-superhero/scripts/extract_voice_codex.py \
  --samples skills/copywriter-superhero/references/voice-samples-<brand> \
  --out skills/copywriter-superhero/references/voice-codex-<brand>.json --print

python3 skills/copywriter-superhero/scripts/score_copy.py draft.md \
  --regime short-form --codex skills/copywriter-superhero/references/voice-codex-<brand>.json
```

The codex gives measured sentence rhythm, punctuation habits, jargon tolerance, metaphor
frequency, capitalization, signature phrases, protected brand terms, and soft-banned words
the brand used once.

Two rules about how voice interacts with discipline:

- **In short-form, long-form, and editorial, the codex governs the style gates.** Brand
  rhythm replaces the profile default.
- **In microcopy and functional, the profile always wins.** Clarity law outranks brand
  personality on a button and in a contract. Protected brand terms are still honoured.

**Never write the samples yourself.** A codex built from generated copy measures the model,
not the brand. If the brand truly uses a flagged word repeatedly, add a real published
sample proving it and regenerate — the extractor reclaims the word automatically. Editing
a codex by hand desynchronises it from the corpus and it will be overwritten. Details:
[references/voice-codex-template.md](references/voice-codex-template.md).

---

## Step 7 — Hand over, and expect to iterate

The first draft is a starting point, not a submission. Conversational steering is the
expected next move, not a failure state. Close every handover by inviting it.

```markdown
**Regime:** short-form · PAS · problem-aware · cold
**Linter:** PASS (score N/100, M warnings)
**Specificity:** 1–5 — photographable nouns, verifiable numbers
**Mechanism:** 1–5 — does every benefit say why it is true
**Structure fit:** 1–5 — does the framework match the awareness level
**On voice:** 1–5, or "n/a — no codex supplied"
**Recommendation:** which version to ship first, and why

Steer me: "too formal, loosen it" · "lead with the price" · "cut it to 40 words"
· "more Pain, less Logic" · "wrong awareness level, they already know us"
```

**Re-run the linter after every rewrite.** Loosening register is exactly when banned
constructions creep back in.

---

## Boundaries

- **Page structure, section order, HTML, CTA placement** → that is `conversion-architect`.
  Write the copy; do not assemble or style the page here.
- **Deployment, export, shipping to a URL** → that is `json-exporter`. Never run deploy
  commands from this skill.
- **Legal advice** → never. This skill drafts functional documents; a qualified lawyer
  reviews them.
- **Voice codex for a new brand** → build it from that brand's real samples in its own
  directory. Never reuse another brand's codex or blend two corpora.

## Reference index

| File | Read it when |
|---|---|
| [references/frameworks.md](references/frameworks.md) | Every task, at triage. Awareness levels and framework selection |
| [references/microcopy-rules.md](references/microcopy-rules.md) | Regime is microcopy |
| [references/long-form-architecture.md](references/long-form-architecture.md) | Regime is long-form, or deciding long versus short |
| [references/editorial-and-narrative.md](references/editorial-and-narrative.md) | Regime is editorial: books, scripts, essays, speeches |
| [references/functional-and-legal.md](references/functional-and-legal.md) | Regime is functional: terms, policies, help, release notes |
| [references/profiles.json](references/profiles.json) | Checking which gate applies where, or why something blocked |
| [references/buzzword-replacement-table.md](references/buzzword-replacement-table.md) | A linter hit needs a replacement, or adding a rule |
| [references/plain-language-table.md](references/plain-language-table.md) | Cutting legalese and buried verbs |
| [references/funnel-angle-recipes.md](references/funnel-angle-recipes.md) | Drafting angles, or a linter overlap block |
| [references/voice-codex-template.md](references/voice-codex-template.md) | Onboarding a brand voice, or interpreting codex numbers |
| [examples/](examples/) | Calibrating what a passing deliverable looks like per regime |
| [examples/gap-log.md](examples/gap-log.md) | A failure mode recurs and needs a new example pair |

When output fails in a new way, add a concrete example pair to `examples/` and log it in
`gap-log.md`. Do not add another abstract rule. For shape-type failures, examples close the
gap faster than prose.
