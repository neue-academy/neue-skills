# Gap log

Every entry is a failure found by running a **real** brief through the skill. The rule
for closing a gap: if the failure is a *shape* failure, add an example pair. If it is a
*measurement* failure, fix the gate or the table. Never close a gap by adding another
paragraph of abstract advice to `SKILL.md` — prose does not change output shape.

| # | Brief | Failure | Type | Fix |
|---|---|---|---|---|
| 1 | Founding-member waitlist | Generic launch copy: 20 banned words, 4 banned constructions, no angles, 0.72 concrete tokens/100w | shape | Example pair: `bad-output-1.md` vs `good-output-1.md` |
| 2 | Lesson catalogue card | Blocked on flat rhythm at 80 words per angle, even though relative variance was higher than the corpus | measurement | Replaced the absolute stdev gate with a coefficient-of-variation gate |
| 3 | Waitlist launch email | Warned on "breakdowns" x4 across three angles — the offer noun has to appear in each angle | measurement | Protected-term cap now scales with angle count |
| 4 | Waitlist launch email | Interrogative pain opener "Still rebuilding hero sections by hand?" passed the linter | shape | Deliberately not a rule — see below |

---

## Entry 1 — the shape of generic

**Brief:** waitlist launch copy, founding-member offer.

**What a no-codex draft produced:** grammatical, on-topic, dead. Score 0/100. Twenty
banned words, four banned constructions, no angle structure, and 0.72 concrete tokens
per 100 words against a brand floor of 1.00. It described the category ("a
comprehensive solution for creators") instead of the offer (30 breakdowns, 20 tools,
200 seats).

**Why prose would not have fixed it:** the draft was not missing advice, it was missing
commitment. Every sentence hedged because nothing forced a number into it.

**Fix:** the example pair. `bad-output-1.md` and `good-output-1.md` answer the *same
brief*, so the difference is isolated to execution. Read them side by side before
drafting anything new.

## Entry 2 — the variance gate punished short copy

**Brief:** 80-word lesson-catalogue card, `brief-2-lesson-description.md`.

**Failure:** BLOCK on `flat-rhythm`. Sentence-length stdev was 4.96 against a floor of
6.0, so the linter demanded a 25-word sentence inside a 60-word card. Following that
instruction would have made the copy worse.

**Root cause:** the floor was absolute, derived from a corpus containing long compound
FAQ and legal sentences. Absolute variance is not comparable across lengths.

**Fix:** the gate now measures the **coefficient of variation** (stdev ÷ mean), which is
length-invariant. Verified against four samples:

| Sample | cv | Verdict |
|---|---|---|
| Generic AI draft | 0.53 | FAIL (floor 0.54) |
| Brand's own published corpus | 0.71 | pass |
| Passing waitlist copy | 0.81 | pass |
| 80-word catalogue card | 0.77 | pass |

The generic draft still fails, and short copy is no longer punished for being short.

**Lesson:** when a gate blocks copy that is genuinely good, the gate is wrong. Never
distort the copy to satisfy a metric — but never loosen a metric to pass a bad draft
either. Find the length-invariant version of the same idea.

## Entry 3 — protected-term cap ignored angle count

**Brief:** waitlist launch email, `brief-3-launch-email.md`.

**Failure:** WARN on "breakdowns" used four times. But the deliverable was three angles,
each read standalone in a subscriber's inbox. Naming the offer once per angle is correct
copy, and the cap treated the file as one continuous piece.

**Fix:** the cap is now `max_protected_term_repeats × angle_count`. In `--mode single` it
stays at the base value, because a single block genuinely should not repeat a signature
term three times.

## Entry 4 — an interrogative opener that got through, on purpose

**Brief:** waitlist launch email.

**Observation:** the Pain subject line "Still rebuilding hero sections by hand?" is a
question, and Table B bans `are you (tired|struggling|ready)`. The general pattern
evaded the specific regex.

**Decision: not a rule.** A blanket ban on question subject lines would be wrong —
questions genuinely earn opens in email, where the subject's job is to start a thought
the body finishes. The banned form is the *self-pitying* interrogative ("Are you tired
of…"), which presumes the reader's feelings. "Still rebuilding X by hand?" names a
behaviour instead, and the reader can answer it.

**Where the judgment lives instead:** craft rule 4 in `SKILL.md` (open on the reader's
situation) and the "Never open Pain with" list in `references/funnel-angle-recipes.md`.

**Lesson:** not every gap becomes a rule. A regex that fires on good copy costs more
than one that misses a borderline case, because a linter the agent learns to override is
worse than no linter.

---

## Adding an entry

1. Run the real brief. Save the failing output next to the passing one.
2. Classify: **shape** failure (wrong form, missing element) or **measurement** failure
   (gate misfired, table missing a term).
3. Shape → add an example pair answering the same brief. Measurement → fix the gate in
   `scripts/extract_voice_codex.py` or the table, then re-verify against **all** existing
   examples with `scripts/selftest.sh`. A gate change that breaks an old example is a
   regression, not a fix.
4. Add the row to the table above with the fix.
