# Microcopy rules (UX writing)

For buttons, error messages, empty states, tooltips, form labels, placeholders,
confirmations, toasts, and onboarding strings. 1–15 words.

**Sales-copy instincts destroy microcopy.** Persuasion, cleverness, and length are
liabilities here. A user reading a button label is mid-task, not browsing. Every extra
word is read by everyone and helps no one.

Enforced by `score_copy.py --regime microcopy`, which checks each item against its own
kind's rules. Limits live in [profiles.json](profiles.json) under `microcopy_kinds`.

---

## The 3 C's, in strict order

Nielsen Norman Group's ordering is not a list of equals. It is a priority chain.

1. **Clarity** — can it be understood on the first read, with no context?
2. **Concision** — is every word doing work?
3. **Character** — does it sound like the product?

**Apply them in that order and never trade down.** Clever-but-unclear fails regardless of
personality. Character is the last 5%, applied only after the string is already
unambiguous and tight. Most bad microcopy is character applied first.

## The 3 I's — what a string is for

Every string does at least one of these. Know which before writing it.

- **Inform** — tell the user what is true, what happened, or what will happen.
- **Influence** — help the user choose. Reduce hesitation at a decision point.
- **Interact** — label an action so the user can predict its result.

A string trying to do all three usually does none. Pick the primary job.

---

## Output format

Label every string with its kind so the rules can be applied and checked:

```markdown
### Button — save draft
Save draft

### Error — email missing @
That email address is missing an "@". Add it and try again.

### Empty state — no projects yet
No projects yet. Create your first one to see it here.
```

The kind before the dash drives the rules. The context after the dash is where the string
appears — without it, nobody can review whether the string is right.

---

## Buttons and CTAs — 1–4 words

| Rule | Why | Bad | Good |
|---|---|---|---|
| Start with a verb | The label must predict the result | "Account creation" | "Create account" |
| Name the outcome, not the mechanism | Users think in goals | "Submit" | "Send message" |
| Match the heading's noun | Continuity confirms they are in the right place | "Continue" under "Delete workspace" | "Delete workspace" |
| Never ask a question | A question asks permission; a button takes action | "Ready to start?" | "Start free trial" |
| Never "Learn more" alone | Says nothing about the destination | "Learn more" | "See pricing" |
| Sentence case | Title Case slows scanning | "Create New Project" | "Create new project" |

**Destructive actions name the object.** "Delete" is a gamble; "Delete 4 files" is a
decision. In a confirmation dialog, the button repeats the verb from the title — never
"OK", which forces the user to re-read the title to know what OK means.

## Error messages — the exact formula

```
[what went wrong] + [why, if known] + [how to fix it]
```

The third part is the one that gets skipped, and it is the only part the user needs.

**Never blame the user.** Delete "you did", "you didn't", "you failed", "you entered".
The system failed to accommodate an input; that is a design fact, not a user error.

**Banned openers:** "Oops", "Invalid", "Error occurred", "Something went wrong" —
when used alone. Each names a feeling, not a cause, and offers no recovery.

Tone is calibrated to severity, and only to severity:

| Severity | Tone | Example |
|---|---|---|
| Minor, recoverable | Neutral, matter-of-fact | "That code has expired. Request a new one." |
| System fault | Apologetic, owns it | "We couldn't save your changes. We're on it — try again in a minute." |
| Data at risk | Calm and urgent, no jokes | "Your last 3 edits aren't saved. Reconnect to save them." |
| Security | Precise, never humorous | "That password was found in a known breach. Choose a different one." |

**Humour scales inversely with stakes.** A playful 404 is fine. A playful payment failure
costs trust at the exact moment trust is being measured.

## Empty states — the most wasted screen in software

An empty state is not an absence. It is the best onboarding moment you will get, because
the user is looking directly at it and wants something to happen.

Three parts: **what belongs here** + **why it is empty** + **one action to fill it.**

- Bad: "No data."
- Good: "No projects yet. Create your first one to see it here."

If the emptiness is a filter result rather than a true zero state, say so and offer the
escape: "No projects match 'archived'. Clear filters."

## Labels, placeholders, tooltips

- **Labels are permanent.** Never use a placeholder as the label — it vanishes on focus,
  taking the user's only reference with it, and it fails screen readers.
- **Placeholders show format, not instruction.** "+44 7700 900123", not "Enter your
  phone number".
- **Tooltips explain, they do not hide.** If information is required to complete the
  task, it belongs on the page. A tooltip is for the 10% who want more.
- **Ask for what you need, once.** Every field costs completions. "Company size" needs a
  justification before it needs a label.

## Confirmations and success states

- Confirm the **object and the consequence**: "Workspace deleted. 12 projects were
  removed." Not "Success!"
- If the action is reversible, say so and how: "Draft archived. Undo".
- If it is irreversible, say that **before** the action, in the dialog, not after.

---

## Length and comprehension

| Sentence length | Comprehension |
|---|---|
| Under 8 words | Effectively complete |
| Under 14 words | About 90% |
| Over 25 words | Falls away sharply |

NN/g's rewriting research found concise, objective, scannable text can improve measured
usability by up to **124%** versus promotional prose. The three edits compound: cut the
word count, strip the marketing tone, make it scannable.

The linter enforces a mean of 12 words and a Flesch–Kincaid grade of 8 for this regime.
Grade 8 is not condescension — it is what a competent adult reads reliably while
distracted, which is the actual condition of every user of every interface.

## Words to strike on sight

| Strike | Use |
|---|---|
| Please (in labels and buttons) | Nothing. It pads every string and means nothing |
| Simply, just, easily | Nothing. If it were easy, saying so would be unnecessary; if it is not, this is an insult |
| Utilize | Use |
| Kindly | Nothing |
| We're sorry for any inconvenience | Say what went wrong and what happens next |
| Are you sure? | Name the consequence: "Delete 4 files? This can't be undone." |
| Click here | The destination: "See pricing" |
| Loading… (alone) | What is loading: "Checking your card…" |
