# Long-form persuasion architecture

For sales pages, VSL scripts, long email sequences, webinar scripts, and direct-mail
letters. 1,500–12,000+ words.

The ten stages below are **required and ordered**. `score_copy.py --regime long-form`
parses your `##` headings and BLOCKs on a missing or out-of-order stage, because long-form
copy that skips a stage loses the reader at exactly that stage — and every stage exists to
answer a question the reader is already asking silently.

---

## First: should this be long at all?

Decide before writing. Getting this wrong produces the two most common AI copy failures:
padding a simple offer into bloat, and under-explaining an expensive one.

**Go long (3,000–10,000+ words) when any two of these are true:**

- Price is above roughly $100, or the commitment is longer than a month
- Traffic is cold — they arrived from an ad or a search, not from knowing you
- The product is complex, new, or uses a mechanism the reader has not seen
- The market is crowded and you must differentiate against named alternatives
- The purchase carries social or professional risk for the buyer

**Stay short (under 300 words) when:**

- The audience is warm and already trusts you
- The decision is low-risk or reversible (free trial, newsletter, waitlist)
- The offer is familiar and needs no explanation
- You are asking for a micro-commitment, not money

**The rule behind the rule:** copy must be exactly as long as the objections require. Not
one word longer. Length is never a goal; it is the cost of clearing every objection
between the reader and the ask. List the objections first, then write the copy that
retires each one. If an objection has no section, the copy is too short. If a section
retires no objection, cut it.

---

## The ten stages

Each stage below lists what it must contain and the reader question it answers.

### 1. Headline
*Reader: "Is this for me?"*

One specific, falsifiable promise. Names the reader or their situation, and the outcome.

- Lead with the outcome plus the constraint: "Ship a landing page in an afternoon —
  without a designer."
- Falsifiable beats bold. "Cut rebuild time from 40 minutes to 4" survives scrutiny;
  "Transform your workflow" does not.
- No questions. No "Introducing". No brand name in the first five words.

### 2. Opening hook
*Reader: "Why should I keep reading?"*

One paragraph, maximum four sentences. A scene, a number, or an admission. It earns the
next line and nothing more.

The strongest hooks are: a dated specific ("Last March I deleted 4,000 lines of my own
code"), a counter-consensus claim, or a cost the reader has been paying without noticing.

Never open with a definition, a dictionary quote, "In today's fast-paced world", or the
reader's job title.

### 3. Problem and agitation
*Reader: "Do they actually understand my situation?"*

Name the problem more precisely than the reader could name it themselves. That precision
is the entire credential — it proves you have been where they are.

Then agitate by **compounding the cost**, never by insulting the reader:

- First-order: the thing that happens.
- Second-order: what that thing costs them in money, hours, or standing.
- Third-order: what it costs if nothing changes for another year.

Agitation is arithmetic, not drama. "Six hours a week is 39 working days a year" does more
than any adjective.

### 4. Credibility bridge
*Reader: "Why should I listen to you specifically?"*

Two to four sentences. Empathy first, then authority. Earned specifics only: numbers,
years, named clients, a public artefact someone can check.

This is a bridge, not a biography. It exists to buy permission for the mechanism reveal
that follows. Any sentence here that does not increase trust is theft from the reader's
attention.

### 5. Mechanism reveal
*Reader: "Why would this work when nothing else did?"*

The single most under-written stage, and the one that separates good long-form from a long
list of benefits.

Name the mechanism. Explain **why it works**, structurally — the causal chain, not the
result. Then explain why the alternatives fail for a reason that is not "they're bad": a
structural limitation the reader can verify against their own experience.

A named mechanism is memorable and repeatable. Unnamed mechanisms read as opinion.

### 6. Proof stack
*Reader: "Says who?"*

Four types, in descending order of strength. Use at least three.

1. **Measured results** — before and after, with the method stated. Strongest.
2. **Case studies** — one named customer, their starting point, what changed, in their
   words where possible.
3. **Testimonials** — attributed, specific, and about the outcome rather than the vibe.
   "Great product!" is worth less than no testimonial, because it signals you had nothing
   better.
4. **Credentials and third-party signals** — audits, counts, logos, press. Weakest alone,
   useful as reinforcement.

Proof must map to the objections raised in stage 3. Proof that answers a question nobody
asked is padding.

### 7. Offer presentation
*Reader: "What exactly do I get, and what does it cost?"*

Full stack, itemised. Deliverables, quantities, access terms, timelines, price.

- Value-anchor before the price, and anchor against a real alternative — what the reader
  would otherwise spend in money or hours.
- One price, stated plainly. Never "investment", never "only".
- If there are tiers, three at most, with one marked as the recommendation and a reason.
- State what is *not* included. Naming the limit raises belief in everything else.

### 8. Risk reversal and guarantee
*Reader: "What happens if this doesn't work for me?"*

Name the guarantee, its duration, and the exact steps to claim it. Vague guarantees
transfer risk *to* the reader.

Address the unspoken fear too: switching cost, wasted time, looking foolish for having
bought it. The refund covers the money; the copy has to cover the rest.

### 9. Urgency and close
*Reader: "Why now?"*

The reason to act must be **real**: a dated cohort, a price change, a capacity limit, a
closing enrolment. Manufactured scarcity is detected instantly and costs more than it
earns.

Then the ask: one imperative CTA naming the outcome, with friction pre-answered — what
happens next, how long it takes, what card details are needed. Repeat the primary CTA
verbatim; competing CTAs split intent.

If there is genuinely no deadline, use the cost of delay from stage 3 instead. Never
invent a countdown.

### 10. Postscript
*Reader (skimmer): "Just tell me the point."*

The P.S. is read by people who read nothing else, which makes it the second most valuable
paragraph on the page. Use it for one of:

- The single strongest proof point, restated
- The guarantee, restated in one line
- The deadline and the ask
- The one objection you know is still standing

Never use it for a summary. One P.S., occasionally two. Never three.

---

## Craft rules that apply across all ten stages

**Every section transition is a fresh open.** Readers leave at section boundaries. The
first sentence after each heading must re-earn attention on its own, without depending on
the sentence before it.

**One idea per paragraph, three sentences maximum.** Long-form reads long on a phone
before it reads long in a word count.

**Subheads must carry the argument alone.** A reader scanning only your `##` lines should
arrive at the offer already half-convinced. If your subheads are labels ("Features",
"About us"), the skim path is dead.

**Bullets prove, prose persuades.** Bullets for specifications and deliverables; prose for
mechanism and story. A page that is all bullets has no argument, only inventory.

**Specificity beats intensity, everywhere.** "Cut it to 4 minutes" outperforms "radically
faster" at every stage. The linter enforces a floor of concrete tokens for this reason.

**Voice comes last.** Structure, then argument, then sentences, then brand voice. Applying
voice earlier just produces on-brand copy with no spine.

---

## Long email sequences

A sequence is one long-form argument distributed across sends. Do not restart the
architecture in every email.

| Email | Stage carried | Ask |
|---|---|---|
| 1 | Hook + problem | Read the next one |
| 2 | Agitation + credibility | Soft click |
| 3 | Mechanism reveal | Soft click |
| 4 | Proof stack | Direct ask |
| 5 | Offer + guarantee | Direct ask |
| 6 | Urgency + close | Direct ask, deadline named |

Each email needs its own hook and its own close. Only the middle changes.
