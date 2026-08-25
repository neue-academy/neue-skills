# Plain-language replacement table

Loaded **in addition** to `buzzword-replacement-table.md` when the regime is
`functional` (terms of service, privacy policies, contracts, policy docs, transactional
email, help articles, release notes).

Parsed by the same reader, so the format is identical: Table A is words, Table B is
constructions, a literal `|` in a cell is written `\|`.

**What this list is not.** It does not touch terms of art that carry settled legal
meaning — *force majeure*, *indemnify*, *joint and several*, *without prejudice*,
*consideration*, *material breach*. Those stay. What it removes is bloat with no legal
effect: doublets, archaic pointers, and buried verbs. Shorter is not less binding.

**When a lawyer overrules a row here, the lawyer wins.** Record it in the handover and
move on. Precision outranks readability in this regime; the two only conflict rarely,
and this table targets the cases where they do not conflict at all.

---

## Table A — Legal and bureaucratic bloat

| Banned | Replace with |
|---|---|
| hereinafter | Name the thing once, then use that name |
| aforementioned | "the [thing] above", or name it |
| aforesaid | Name it |
| herein | "in this agreement" — or name the section |
| hereof | "of this agreement" |
| hereto | Name the parties or the document |
| hereunder | "under this agreement" |
| thereof | "of it", or name the thing |
| thereto | Name the thing |
| therein | Name the document or section |
| thereunder | Name what it is under |
| whatsoever | Delete |
| hereby | Delete. The sentence does the work without it |
| duly | Delete |
| forthwith | Give the actual deadline: "within 5 business days" |
| pursuant to | "under" |
| prior to | "before" |
| subsequent to | "after" |
| in the event that | "if" |
| in the event of | "if" |
| in the event | "if" |
| at this point in time | "now" |
| for the purpose of | "to" |
| for the purposes of | "to" |
| with respect to | "about", or name the relationship |
| with regard to | "about" |
| in relation to | "about" |
| in accordance with | "under", or "as set out in [section]" |
| is required to | "must" |
| is obligated to | "must" |
| is entitled to | "may" |
| is permitted to | "may" |
| in the amount of | "of" |
| on a monthly basis | "monthly" |
| on an annual basis | "annually" |
| make a determination | "decide" |
| makes a determination | "decides" |
| give consideration to | "consider" |
| provide notification | "notify" |
| provide notice | "notify", and say how |
| is applicable to | "applies to" |
| have knowledge of | "know" |
| has knowledge of | "knows" |
| in a timely manner | Give the deadline |
| as soon as practicable | Give the deadline |
| as soon as reasonably possible | Give the deadline |
| including but not limited to | "including" — the list is already non-exhaustive |
| including without limitation | "including" |
| and/or | Pick one, or write "A, B, or both" |
| inter alia | "among other things" |
| ab initio | "from the start" |
| mutatis mutandis | Spell out which changes apply |
| null and void | "void" |
| cease and desist | "stop" |
| each and every | "each" |
| any and all | "all" |
| sole and exclusive | "sole" |
| free and clear | "free" |
| full and complete | "complete" |
| true and correct | "correct" |
| terms and conditions | "terms" |
| commence | "start" |
| commences | "starts" |
| terminate | "end" — reserve "terminate" for the defined contractual act |
| endeavour | "try" |
| endeavor | "try" |
| utilise | "use" |
| effectuate | "carry out" |
| render assistance | "help" |
| afford an opportunity | "let" |
| at the discretion of | "chosen by" — and name who chooses |
| notwithstanding | "despite", or "even if" |
| heretofore | "until now" |
| whereas | Delete, or state the fact plainly |

---

## Table B — Constructions that hide the actor or the obligation

| Regex | Why it reads as bureaucratic | Rewrite instruction |
|---|---|---|
| `\bshall\b` | Ambiguous: obligation, permission, or futurity? Courts have split on it | "must" for an obligation, "will" for the future, "may" for permission |
| `\bshall not be (deemed\|construed\|considered)\b` | Triple-negative reasoning | "does not mean" |
| `\bit is (agreed\|understood\|acknowledged) that\b` | The whole document is agreed | Delete the clause, keep the fact |
| `\bnothing (herein\|in this)\b.{0,60}?\b(shall\|will)\b` | States the rule by negation | State what the provision does do |
| `\bfor the avoidance of doubt\b` | Signals the previous sentence is ambiguous | Fix the ambiguous sentence, then delete this one |
| `\bwithout limiting the (generality\|foregoing)\b` | Pre-emptive hedge with no content | Delete, or state the limit you mean |
| `\bas the case may be\b` | Leaves the reader to enumerate the cases | Name the cases |
| `\bto the extent (that\|permitted)\b` | Vague conditional | "if", "when", or name the limit |
| `\bunless and until\b` | Doublet | "until" |
| `\bif and only if\b` | Doublet | "only if" |
| `\bthe part(y\|ies) (of the first part\|hereto)\b` | Archaic naming | Name them: "you" and "Revelium" |
| `\bsubject to the provisions of\b` | Buried cross-reference | "under [section]" |
| `\bshall be \w+ed by\b` | Passive with the actor demoted to the end | Put the actor first: "X must do Y" |
| `\bwe reserve the right to\b` | Padding around a simple permission | "we may" |
| `\bthere (is\|are) no \w+ (that\|which)\b` | Existential negation | State the positive rule |
| `\bin the case where\b` | Wordy conditional | "if" |
| `\bat all times\b` | Adds no obligation | Delete, or give the period |
| `\bfrom time to time\b` | Unbounded and unenforceable | Give the frequency or the trigger |
| `\bmake (application\|payment\|provision) (for\|to)\b` | Buried verb | "apply", "pay", "provide" |
| `\bis in (compliance\|violation) with\b` | Buried verb | "complies with", "breaks" |

---

## Structural rules the tables cannot check

Apply these by hand; they matter more than any single word.

1. **Second person, present tense.** "You must give 30 days' notice" beats "The
   Subscriber shall be required to provide notice of not less than 30 days".
2. **One obligation per sentence.** If a sentence contains two "must"s, split it.
3. **Define once, at first use, then never redefine.** A term defined twice is a
   litigation risk.
4. **Number and title every section.** Readers arrive by search, not from the top.
5. **Lead each section with its rule**, then the exceptions. Never the reverse.
6. **Replace cross-references with the content** when the content is under 20 words.
   "as described in Section 12.4(b)" costs the reader a round trip.
7. **Tables beat prose** for anything with more than three conditions.
8. **Keep the reading grade at or below 12**, and below 9 for anything consumer-facing.
   The linter measures this. A document nobody can read is a document nobody consented to.
