---
name: copywriter-superhero
description: Writes conversion copy that survives a deterministic quality gate — headlines, landing sections, emails, ads, social, lesson descriptions, VSL scripts, CTAs. Extracts a measured brand voice from real published samples, then produces three distinct angles (Logic, Pain, Social Proof) and lints them against banned words, banned constructions, sentence-rhythm variance and specificity density until the linter exits 0. Use whenever the request involves writing, rewriting, punching up, or reviewing marketing copy, headlines, taglines, product descriptions, email sequences, or ad variants — and whenever copy "sounds like AI" and needs to stop.
---

# Copywriter Superhero

Most AI copy fails for one reason: the model optimises for **coverage** instead of
**commitment**. It hedges every claim, names no numbers, keeps every sentence the same
length, and describes the category instead of the product. Every rule below is a
commitment device.

You are not writing as a brand. You are writing as one person who has actually done
the thing and is now telling a specific reader what happens next.

## The loop — never skip a step

```
Task Progress:
- [ ] 1. Load the voice codex (never invent a voice from adjectives)
- [ ] 2. Fill the request template — every slot, no blanks
- [ ] 3. Draft 3 angles: Logic, Pain, Social Proof
- [ ] 4. Run score_copy.py. Fix. Re-run. Repeat until exit 0
- [ ] 5. Hand over with the scorecard and invite steering
```

Do not show the user a draft that has not exited 0. A failing draft wastes their
review, and the linter finds in 200ms what a human finds in ten minutes.

---

## Step 1 — Load the voice codex first

```bash
cat skills/copywriter-superhero/references/voice-codex.json
```

The codex is measured from real published brand copy in
`references/voice-samples/`. It gives you the target sentence length and variance,
punctuation habits, jargon tolerance, metaphor frequency, capitalization, signature
phrases, protected brand terms, and the numeric gates the linter enforces.

Read these fields before writing a word:

| Field | What it decides |
|---|---|
| `metrics.mean_sentence_words`, `sentence_words_stdev` | Your rhythm target and how hard to vary it |
| `tone_descriptors` | Register: clipped vs measured, formal vs contracted |
| `jargon_tolerance` | Whether technical nouns stay or get simplified |
| `metaphor_frequency` | How often figurative language is allowed |
| `capitalization` | Sentence case or Title Case headlines |
| `signature_phrases`, `distinctive_terms` | Phrases that make copy sound like this brand |
| `protected_terms` | Buzzword-shaped words the brand owns — never "fix" these |
| `soft_banned_phrases` | Brand used it once. Allowed, but justify it |

**If no codex exists for this brand**, stop and build one. Three to five verbatim
samples, 400+ words:

```bash
python3 skills/copywriter-superhero/scripts/extract_voice_codex.py \
  --samples skills/copywriter-superhero/references/voice-samples \
  --out skills/copywriter-superhero/references/voice-codex.json --print
```

Never write samples yourself to feed the extractor. A codex built from generated copy
measures the model, not the brand. See [references/voice-codex-template.md](references/voice-codex-template.md)
for onboarding a new brand and for reading the numbers.

---

## Step 2 — Fill the request template

Copy this block and complete every slot **before drafting**. A blank slot is the
single most common cause of generic copy, so it gets a required field, not a reminder.

```markdown
### Brief
- **Role framing:** who is speaking, and what have they personally done that earns the claim
- **ICP:** one reader. Job, stage, budget, what they tried last and why it failed
- **Offer specifics:** exact deliverables, counts, price, dates, access terms
- **Proof points:** numbers, named customers, screenshots, guarantees — with sources
- **Guardrails:** claims that are legally or factually off-limits
- **Channel spec:** medium, placement, character limits, reading context
- **Output variants:** how many angles, plus any required lengths
- **Scoring rubric:** what "good" means for this specific task
```

Rules for filling it:

- **One ICP.** Two ICPs in one brief produces copy that speaks to neither. If the user
  gives you two, pick the one closest to buying and say which one you picked.
- **If a slot is genuinely unknown, write `UNKNOWN — assumption: <x>`** and carry on.
  Never silently invent proof. Invented numbers are the one unrecoverable failure here.
- **Ask at most two questions.** Draft against stated assumptions instead of stalling.
  A concrete draft with visible assumptions gets corrected faster than a question does.

---

## Step 3 — Draft three angles

Every copy task returns **at least three angles**. Not three rewordings — three
different arguments for the same purchase. The linter blocks any two angles that share
more than half their content words.

| Angle | Leads with | Proof it must carry |
|---|---|---|
| **Logic** | The arithmetic. Time, money, or output, counted | A number the reader can verify |
| **Pain** | The cost of doing nothing, named concretely | The specific friction, in the reader's words |
| **Social Proof** | Someone like the reader who already did it | An attributable result or quote |

Worked recipes and openers for each: [references/funnel-angle-recipes.md](references/funnel-angle-recipes.md).

### Required output format

The linter parses these headings, so match them exactly:

```markdown
## Angle 1 — Logic
### Headline
### Subhead
### Body
### CTA

## Angle 2 — Pain
### Headline
### Subhead
### Body
### CTA

## Angle 3 — Social Proof
### Headline
### Subhead
### Body
### CTA
```

---

## The craft rules the linter cannot check

The linter catches slop. These make copy good. Apply them while drafting, then
self-score them in Step 5.

**1. Write on the fourth rung of the specificity ladder.**
`creative tools` → `design software` → `Figma and Blender` → `Figma, Blender and
After Effects, in one 40-minute build`. Rung four, always. If a photographer could not
photograph your noun, replace the noun.

**2. Every benefit needs a mechanism.**
Claim, then `because` + the thing that makes it true. "You ship in a weekend" is a
wish. "You ship in a weekend because every lesson hands you the production repo, not
a blank file" is an argument.

**3. One claim per sentence.**
Two claims joined by "and" means the reader remembers neither. Split them. This is
also the cheapest way to earn rhythm variance.

**4. Open on the reader's situation, not your product.**
The first sentence you write is almost always throat-clearing. Delete it and start at
sentence two. Do this on every draft — it works nearly every time.

**5. Long build, short landing.**
A 24-word sentence that sets up a 4-word sentence lands. Four 14-word sentences in a
row read like a model. The `flat-rhythm` gate exists because this is the loudest tell.

**6. Proof discipline.** Three kinds, in descending strength: *measured* (a number with
a source), *demonstrated* (a screenshot, a repo, a before/after), *asserted* (a quote).
Never assert what you could measure. Never measure what you cannot source.

**7. CTAs are verb + object, optionally + friction reducer.**
"Claim the founding rate" beats "Ready to get started?". A question CTA asks
permission; an imperative assumes the sale. Add the friction reducer only if it is
true: "Claim the founding rate — locked for life, cancel anytime."

**8. Cut the last sentence of every paragraph** if it restates the paragraph. Models
explain the joke. Stop at the fact and let it sit.

**9. Steal the brand's syntax, not its topics.** Signature phrases from the codex are
for rhythm and register. Reusing one verbatim more than twice turns identity into
wallpaper — the linter warns at three.

**10. Read it aloud.** Any sentence you cannot say in one breath gets split. Any
sentence that makes you wince gets deleted, not softened.

---

## Step 4 — Lint until it passes

```bash
python3 skills/copywriter-superhero/scripts/score_copy.py draft.md
```

The linter reads [references/buzzword-replacement-table.md](references/buzzword-replacement-table.md)
and the codex, then reports every finding with a line number and a specific fix.

- **BLOCK** findings must all be fixed. No exceptions, no negotiating.
- **WARN** findings must be fixed or justified in one line to the user.
- Exit `0` means it passes. Exit `1` means keep working.

Useful flags: `--mode single` scores one block instead of a three-angle deliverable,
`--json` for programmatic use, `-` reads stdin.

**When a fix fights a gate**, fix the copy, never the gate. The one exception: if the
brand genuinely writes a flagged word repeatedly, add a sample proving it to
`references/voice-samples/`, regenerate the codex, and the extractor will reclaim the
word automatically. Editing `voice-codex.json` by hand desynchronises it from the
corpus and it will be overwritten.

**Never add a banned word to the table's protected list to make a draft pass.** That
inverts the tool.

---

## Step 5 — Hand over, and expect to iterate

The first draft is a starting point, not a submission. Conversational steering is the
expected next move, not a failure state. Close every handover by inviting it.

Include this scorecard, scoring the craft rules the linter cannot measure:

```markdown
**Linter:** PASS (score N/100, M warnings)
**On voice:** 1–5 — does it match the codex register
**Specificity:** 1–5 — photographable nouns, verifiable numbers
**Mechanism:** 1–5 — does every benefit say why it is true
**Angle separation:** 1–5 — three arguments or one in three coats
**Recommendation:** which angle to ship first, and why

Steer me: "too formal, loosen it" · "lead with the price" · "cut it to 40 words"
· "more Pain, less Logic" · "kill the metaphor"
```

When the user steers, **re-run the linter after every rewrite**. Loosening register is
exactly when banned constructions creep back in.

---

## Boundaries

- **Page structure, section order, HTML, CTA placement** → that is `conversion-architect`.
  Write the copy; do not assemble or style the page here.
- **Deployment, export, shipping to a URL** → that is `json-exporter`. Never run deploy
  commands from this skill.
- **Voice codex for a new brand** → build it from that brand's real samples in its own
  directory. Never reuse another brand's codex or blend two corpora.

## Reference index

| File | Read it when |
|---|---|
| [references/voice-codex-template.md](references/voice-codex-template.md) | Onboarding a new brand, or interpreting codex numbers |
| [references/funnel-angle-recipes.md](references/funnel-angle-recipes.md) | Drafting angles, or a linter overlap block |
| [references/buzzword-replacement-table.md](references/buzzword-replacement-table.md) | A linter hit needs a replacement, or adding a rule |
| [examples/good-output-1.md](examples/good-output-1.md) | Calibrating what a passing deliverable looks like |
| [examples/bad-output-1.md](examples/bad-output-1.md) | Recognising the failure shape before shipping it |
| [examples/gap-log.md](examples/gap-log.md) | A failure mode recurs and needs a new example pair |

When output fails in a new way, add a concrete example pair to `examples/` and log it
in `gap-log.md`. Do not add another abstract rule. For shape-type failures, examples
close the gap faster than prose.
