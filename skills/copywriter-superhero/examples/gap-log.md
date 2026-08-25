# Gap log

Every entry is a failure found by running a **real** brief through the skill. The rule
for closing a gap: if the failure is a *shape* failure, add an example pair. If it is a
*measurement* failure, fix the gate or the table. Never close a gap by adding another
paragraph of abstract advice to `SKILL.md` — prose does not change output shape.

| # | Brief | Failure | Type | Fix |
|---|---|---|---|---|
| 1 | Founding-member waitlist | Generic launch copy: 20 banned words, 4 banned constructions, no angles, 0.72 concrete tokens/100w | shape | Example pair: `bad-short-form.md` vs `good-short-form.md` |
| 2 | Lesson catalogue card | Blocked on flat rhythm at 80 words per angle, even though relative variance was higher than the corpus | measurement | Replaced the absolute stdev gate with a coefficient-of-variation gate |
| 3 | Waitlist launch email | Warned on "breakdowns" x4 across three angles — the offer noun has to appear in each angle | measurement | Protected-term cap now scales with angle count |
| 4 | Waitlist launch email | Interrogative pain opener "Still rebuilding hero sections by hand?" passed the linter | shape | Deliberately not a rule — see below |
| 5 | App error messages | One rulebook for all copy: marketing gates judged a 3-word button, and microcopy rules had no way to fire | shape | Five regime profiles in `profiles.json`, routed by a triage step |
| 6 | App error messages | "Ask the owner for a new one" read as having no recovery step, and the last item swallowed 200 words of trailing prose | measurement | Widened the imperative verb list; item bodies now stop at the next heading; only labelled strings are scored |
| 7 | Plain-language terms excerpt | Buried-verb gate flagged "critical", "liability", "typical" — adjectives and legal nouns with no verb to restore | measurement | Dropped bare `-al` and `-ity` from the detector; listed the real `-al` nominalizations explicitly |
| 8 | Contractor sales letter | Auto-detection routed a 1,257-word sales letter as short-form, because its `## Proof` stage matched the angle-heading pattern | measurement | Detection needs two distinct angles; single-stage matches no longer count |

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

**Fix:** the example pair. `bad-short-form.md` and `good-short-form.md` answer the *same
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

**Fix:** the cap is now `max_protected_term_repeats × angle_count`. With `--variants 1` it
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

## Entry 5 — one rulebook cannot govern five jobs

**Brief:** error messages, button labels, and empty states for a render app.

**Failure:** the skill had a single set of gates, calibrated on marketing copy. A 3-word
button was measured for sentence-rhythm variance, which is meaningless at three words.
Nothing checked the one thing that mattered: whether the error told the user how to
recover. The skill was a brand-voice tool wearing a copywriting label.

**Root cause:** the entry point was the brand, not the job. Voice-codex-first design
assumes every task starts from brand samples, but UX writing and long-form direct response
follow well-documented rules that have nothing to do with brand voice.

**Fix, three parts.** Five regime profiles in `references/profiles.json`, each declaring
which checks run and at what severity. A mandatory triage step that states the regime,
awareness level, and traffic temperature before drafting. Brand voice demoted to an
optional last filter, with a default codex so the linter works with zero brand input.

**Proof it worked:** `good-long-form.md` exits 0 under `--regime long-form` and exits 1
under `--regime microcopy`. `good-microcopy.md` does the reverse. Both assertions are in
`scripts/selftest.sh`, because a routing system that cannot fail the wrong route is not
routing anything.

## Entry 6 — the microcopy checker judged the wrong text

**Brief:** the same error-message set, `good-microcopy.md`.

**Failures, both from the same cause:** the last labelled string absorbed every following
paragraph, so a 3-word toast was reported as "231 words (max 15)". And the surrounding
craft notes were measured for passive voice, which blocked the file on prose that was never
copy.

**Fix:** an item body now ends at the next heading of any level. When labelled items exist,
everything outside them is masked out before scoring — masked rather than sliced, so
reported line numbers still point at the real file. Separately, "Ask", "Show", "Create",
"Choose" and 60 more imperatives joined the verb list, which had been built for marketing
CTAs and was too narrow to recognise real interface copy.

**Lesson:** a linter that scores the annotation instead of the artefact teaches the agent
to distrust it. Define the scoreable region explicitly.

## Entry 7 — the buried-verb gate caught adjectives

**Brief:** plain-language terms of service, `good-functional.md`.

**Failure:** the nominalization detector matched any word ending `-tion`, `-ment`, `-ity`,
`-ness` or `-al`. That swept up "critical", "typical" and "practical" — adjectives, not
buried verbs — and "liability", a legal noun with no verb to restore. In legal text the
false-positive rate was high enough to make the gate unusable.

**Fix:** dropped bare `-al` and `-ity` from the pattern, and listed the `-al` words that
genuinely are nominalizations ("renewal", "approval", "removal", "referral") explicitly.
The gate now targets what it was always for: a verb turned into a noun, usually propped up
by a weak verb — "make a determination" instead of "decide".

**Lesson:** the same one as entry 4. A rule that fires on correct writing costs more than
a rule that misses a borderline case.

## Entry 8 — auto-detection misread a sales letter

**Brief:** contractor sales letter, `good-long-form.md`.

**Failure:** `--regime auto` routed 1,257 words of long-form as short-form, because the
letter's `## Proof` stage matched the angle-heading pattern used by three-angle marketing
deliverables. A single keyword collision sent the whole document to the wrong rulebook.

**Fix:** detection now requires **two** distinct angle headings, since a multi-variant
deliverable has three and a sales letter has one proof stage. The functional detector was
rebuilt on the same principle: well-written policy has no legalese, so it keys on document
furniture — numbered clauses, retention periods, changelog headings — instead.

**Lesson:** detection heuristics need high-precision signals, while scoring can stay
permissive. The two jobs should not share a threshold. The skill still instructs the agent
to pass `--regime` explicitly; auto-detection is a safety net, not the contract.

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
