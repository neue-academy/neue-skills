# Good microcopy — passing example

Regime: microcopy. Awareness: n/a (the user is mid-task, not being sold to).

Verify:

```bash
python3 skills/copywriter-superhero/scripts/score_copy.py \
  skills/copywriter-superhero/examples/good-microcopy.md --regime microcopy
```

The brief: a project workspace app. A user is exporting a render and hits three failure
paths. Every string below is labelled with its kind, because the kind decides the rules.

<!-- Clarity, then concision, then character. In that order, every time. -->

---

### Button — start an export
Export render

### Button — confirm a destructive action
Delete 4 renders

### Button — leave a form with unsaved work
Save and close

### Link — pricing from a plan limit
See plan limits

### Label — project name field
Project name

### Placeholder — project name field
Q3 launch page

### Tooltip — why a render is queued
Renders run one at a time per seat.

### Error — export failed because the file is too large
That file is 240 MB. The limit is 100 MB. Trim it, or export at half scale.

### Error — the render server dropped the job
We lost the render halfway. We charged nothing. Send it again.

### Error — unsaved edits and a dead connection
Your last 3 edits are not saved. Reconnect to save them.

### Error — expired invite code
That code expired on 4 March. Ask the owner for a new one.

### Empty state — no renders yet
No renders yet. Export one to see it here.

### Empty state — a filter matched nothing
No renders match "archived". Clear the filter to see all 12.

### Confirmation — deleting renders
Delete 4 renders? This cannot be undone.

### Success — export finished
Render saved to Downloads. Open it now.

### Toast — a change that can be reversed
Project archived. Undo

---

## Why each of these passes

**Buttons name the outcome, not the mechanism.** "Export render" tells the user what they
get. "Submit" tells them what the form does, which is the developer's problem, not theirs.
The destructive button names the object and the count, so it is a decision instead of a
gamble.

**Errors carry all three parts.** What went wrong, why when it is known, and how to fix it.
The third part is the one that gets dropped, and it is the only one the user needs. Note
the tone shift: neutral for the size limit, apologetic and owning it for the server fault,
calm and urgent for the unsaved edits. Severity sets the tone; nothing else does.

**Nobody is blamed.** "That file is 240 MB", not "You uploaded a file that is too large".
The system failed to accommodate an input. That is a design fact.

**Numbers instead of adjectives.** 240 MB, 100 MB, 3 edits, 4 March, 12 renders. Specifics
cost the same number of words as vagueness and do the work of a paragraph.

**The empty states sell nothing and teach one action.** They also distinguish a true zero
state from a filter result, which is the most common empty-state defect in software.

**The label is permanent and the placeholder shows format.** A placeholder used as a label
vanishes on focus and fails screen readers.

Full rulebook: [../references/microcopy-rules.md](../references/microcopy-rules.md).
