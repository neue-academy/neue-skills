# Conversion anatomy

The section contract, stated as what the page **is**, section by section. Not a
checklist of things to consider — a recipe with a fixed order. The order is the
argument: make the claim, prove it, clear the objection, name the price, ask once.

Every section carries `data-section="<name>"` so `scripts/audit_page.py` can verify
the order mechanically.

---

## 1. `hero` — one message, one ask

**Is:** an eyebrow label, one `h1` making a single claim, one subhead that adds the
mechanism or the number, one primary CTA, and one line of terms under it.

**Contains exactly:**

| Element | Rule |
|---|---|
| Eyebrow | Optional. Names the offer or the moment. Max 8 words, monospace register |
| `h1` | Exactly one on the page. Under 14 words. One claim, not two joined by "and" |
| Subhead | 1–2 sentences. Carries the number or the mechanism the `h1` asserts |
| Primary CTA | Exactly one clickable in this section. `data-cta="primary"` |
| Terms line | Under 12 words. Price, seat count, or cancellation. Never fake scarcity |

**Never contains:** a second CTA, a navigation menu with more than 4 items, a carousel,
a video that autoplays with sound, or a second competing claim.

**The test:** cover everything below the fold. Can a stranger say what this is, who it
is for, and what happens when they click? If not, the hero has failed, and no section
below it can recover the visit.

## 2. `proof` — the claim, verified

**Is:** evidence for the exact claim the `h1` made. Not general credibility.

**Contains:** a figures grid (3–4 numbers, each with a one-line gloss), plus one
attributed quote or one demonstrated artefact (screenshot, repo, deployed URL).

**Rules:**
- Every number needs a gloss naming its unit. `30+` alone is noise; `30+ project
  breakdowns, production repo attached` is proof.
- The quote reports a **result**, never a compliment. "I repriced at €2,400 the same
  month" is proof. "The best course I've taken" is decoration.
- Logo walls are the weakest proof available. Use one only if the logos are customers
  and the reader knows them.

## 3. `objections` — the three reasons people do not buy

**Is:** the three real objections, answered directly, in the reader's words.

**Contains:** 3 blocks, each an `h3` stating the objection as the reader would say it,
then 2–3 sentences answering it with a mechanism.

**Rules:**
- Write the objection as a statement or a question the reader actually thinks: "I have
  never deployed anything." Not "Is this suitable for beginners?"
- Answer with a mechanism, not reassurance. "Each teardown ends at a deployed URL" beats
  "Don't worry, it's beginner-friendly."
- Three is the number. One looks defensive, six reads as a page full of doubt.
- The price objection belongs here if price is the top objection. Otherwise it belongs
  in `offer`.

## 4. `offer` — price and terms, no games

**Is:** what it costs, what arrives, and what the terms are.

**Contains:** the price with its unit, the comparison price if one honestly exists, an
`includes` list of 4–6 items, and optionally one low-emphasis link. No primary CTA here.

**Rules:**
- Every list item is a deliverable, never an adjective. "Production source code for
  every project", not "Premium quality content".
- A struck-through comparison price must be a real price that real people pay or will
  pay. Inventing one is fraud, not copywriting.
- No countdown timers unless the deadline is real and enforced.
- The last item should answer "what happens after I pay".

## 5. `final-cta` — the same ask, once more

**Is:** a repeat of the hero's ask, with the friction removed.

**Contains:** an eyebrow, one `h2`, one short line restating what happens next, the
form or CTA, and one fine-print line.

**Rules:**
- **The primary CTA label is identical to the hero's, word for word.** A different label
  reads as a different offer and the auditor blocks it.
- Ask for one field. Every additional field costs conversions and each one needs a
  reason that survives the question "what do we do with this today".
- The fine-print line handles the last hesitation: what you send, how often, how to stop.

---

## Spacing and layout defaults

Change these only with a reason. They are set so that a page assembled from the contract
looks composed rather than improvised.

| Token | Value | Why |
|---|---|---|
| Section padding block | `clamp(4rem, 9vw, 7.5rem)` | Sections must read as separate arguments |
| Hero padding block | `clamp(5rem, 12vw, 9.5rem)` | The hero gets more air than any other section |
| Page max width | `1080px` | Wider makes headlines wrap unpredictably |
| Body measure | `62ch` | Above ~75ch the eye loses the line return |
| Inline padding | `clamp(1.25rem, 4vw, 3rem)` | Never let text touch a phone edge |
| Card / grid radius | `14px` | One radius token for the whole page |
| Vertical rhythm | `1.1rem` between stacked siblings | One spacing step, applied consistently |
| Grid minimum column | `160px` figures, `270px` prose | Below that, columns collapse into stripes |
| Section divider | `1px solid` at 12% contrast | Structure without drawing attention |

**Type scale** — fluid, so no breakpoint juggling:

| Role | Value |
|---|---|
| `h1` | `clamp(2.6rem, 1.4rem + 5.4vw, 5.1rem)`, tracking `-0.022em`, line-height `1.08` |
| `h2` | `clamp(1.85rem, 1.2rem + 2.2vw, 2.9rem)` |
| `h3` | `1.1rem`, line-height `1.35` |
| Body | `clamp(1rem, 0.95rem + 0.2vw, 1.075rem)`, line-height `1.6` |
| Lede | `clamp(1rem, 0.6rem + 1.4vw, 1.4rem)`, dimmed |
| Eyebrow / label | `0.72rem` monospace, tracking `0.14em`, uppercase |

**Never** set body text below `16px` on mobile — iOS Safari zooms the viewport on focus
for anything smaller, which breaks the layout mid-form.

**Contrast:** body text at or above 4.5:1 against its background, large headings at or
above 3:1. Dimmed text (`--fg-dim`) is the usual failure — check it, do not assume it.
