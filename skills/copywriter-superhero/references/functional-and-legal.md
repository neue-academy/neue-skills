# Functional and legal copy

For terms of service, privacy policies, contracts, transactional email, policy documents,
help articles, and release notes.

> **This skill drafts. It does not advise.** Nothing produced here is legal advice, and no
> contract, policy, or notice should go live without review by a qualified lawyer in the
> relevant jurisdiction. Where a lawyer's wording conflicts with any rule in this file,
> **the lawyer wins** — note the override in the handover and move on.

Run `score_copy.py --regime functional`. This regime loads
[plain-language-table.md](plain-language-table.md) on top of the buzzword table, blocks
passive voice and buried verbs, enforces a reading-grade ceiling, and **does not score
hedging** — "may", "must", and "will" are load-bearing words here, not weakness.

Brand voice never governs this regime. Precision and clarity outrank personality.

---

## The order of priorities

1. **Accuracy.** A clearer sentence that changes the meaning is a defect, not an
   improvement.
2. **Navigability.** Readers arrive by search, at one clause, mid-dispute. They never read
   from the top.
3. **Readability.** Grade 12 ceiling, grade 9 for anything consumer-facing.
4. **Brevity.** Last, and only where it costs nothing above.

Marketing has no place in this regime. Puffery in a binding document is either
unenforceable or a misrepresentation, and it reads as evasive either way.

---

## Sentence-level rules

**Second person, present tense, active voice.**

- Yes: "You must give us 30 days' notice before you cancel."
- No: "Notice of not less than 30 days shall be provided by the Subscriber prior to
  cancellation."

Both bind. One is readable, and readability is now a regulatory expectation in consumer
contexts, not a nicety.

**One obligation per sentence.** Two "must"s in a sentence is two rules that will be
disputed separately.

**Name the actor before the verb.** Passive voice in an obligation creates a duty with
nobody attached to it. "The data will be deleted" — by whom, and by when?

**Use "must" for obligations and "may" for permissions, consistently.** Avoid "shall"; its
meaning has been litigated in both directions and drafting guidance in most jurisdictions
now prefers "must".

**Define a term once, at first use, and never redefine it.** A term defined twice is a
dispute waiting for a plaintiff. Keep defined terms capitalised and few — every definition
is a lookup the reader has to perform.

**Give real numbers, not standards of effort.** "Within 5 business days" is enforceable.
"In a timely manner" and "using reasonable efforts" transfer the argument to a future
court.

---

## Document structure

- **Number and title every section.** Titles are the search index.
- **Lead each section with the rule, then the exceptions.** Never the reverse — a reader
  who stops halfway must stop on the correct default.
- **Inline any cross-reference under 20 words.** "as described in Section 12.4(b)" costs a
  round trip for information you could have repeated.
- **Tables beat prose above three conditions.** Retention periods, tiers, fees, and
  notice windows are all tables.
- **Put a plain-language summary at the top when the document is consumer-facing** — and
  state explicitly that the summary is not the agreement, so it cannot be read as varying
  the terms.
- **Date it and version it.** "Last updated" with the date, plus a changelog for anything
  people have already agreed to.

## Privacy policies specifically

Answer these six questions in this order, because this is the order people ask them:

1. What data do you collect?
2. Why — the specific purpose for each category, not a combined list.
3. Who else sees it — named categories of recipient, and whether they are processors.
4. How long do you keep it — a period or a criterion, per category.
5. What can I do about it — the rights, and the actual mechanism to exercise each.
6. Who do I contact, and how do I complain to a regulator.

A vague purpose ("to improve our services") is the single most common defect. Pair every
category of data with a specific purpose and a retention period, in a table.

## Transactional email

Not marketing. Different rules, and often a different legal basis.

- **Subject line states the event, not a benefit.** "Your invoice for March — $49".
- **The most important fact goes in the first line**, above any greeting.
- **One action, if any.** Transactional email with a marketing CTA risks the legal basis
  it was sent under.
- **Include the reference the reader needs to act**: order number, amount, date, last four
  digits, the deadline.
- **Say what happens if they do nothing.** This is the field most often left out and most
  often needed.

## Help articles

- **Title is the user's question, in their words.** "Why can't I log in?" not
  "Authentication troubleshooting".
- **Answer in the first sentence.** Then the steps. Never build up to the answer.
- **Numbered steps, one action per step**, with the expected result stated for any step
  that can silently fail.
- **State prerequisites and permissions before step one**, not at step four.
- **Screenshots for anything ambiguous**, with alt text describing the action, not the
  image.

## Release notes

- **Group by Added / Changed / Fixed / Removed.** Never one prose paragraph.
- **Write from the user's side.** "Search now matches partial words", not "Refactored the
  indexer".
- **Breaking changes first**, with the migration step inline and a date.
- **No thanking the team in the notes.** Do it elsewhere; the reader came for the change.

---

## Common failures this regime exists to prevent

| Failure | Why it matters |
|---|---|
| Legalese with no legal effect | Doublets and archaisms create ambiguity while sounding rigorous |
| Passive obligations | An obligation with no named actor is unenforceable in practice |
| Standards of effort instead of deadlines | Moves the decision from your document to a court |
| Definitions nobody needs | Every capitalised term is a lookup that lowers comprehension |
| Marketing tone in binding text | Reads as evasive; puffery can become misrepresentation |
| Grade-16 reading level | A document nobody can read is a document nobody meaningfully consented to |
| Undated policies | Nobody can prove what they agreed to, including you |
