# Bad microcopy — failing example

The same three failure paths as [good-microcopy.md](good-microcopy.md), written the way a
model writes them when nobody routed the job. Every string below is what you get when
marketing instincts are applied to an interface.

```bash
python3 skills/copywriter-superhero/scripts/score_copy.py \
  skills/copywriter-superhero/examples/bad-microcopy.md --regime microcopy
```

Exits 1. Keep it that way — this file is the negative test in `scripts/selftest.sh`.

---

### Button — start an export
Submit

### Button — confirm a destructive action
OK

### Button — leave a form with unsaved work
Ready to continue?

### Link — pricing from a plan limit
Click here

### Placeholder — project name field
Enter your project name

### Error — export failed because the file is too large
Oops! Something went wrong.

### Error — the render server dropped the job
Invalid request. Error occurred while the render was being processed by the server.

### Error — unsaved edits and a dead connection
You didn't save your work, so your recent edits might potentially be lost unfortunately.

### Empty state — no renders yet
No data.

### Confirmation — deleting renders
Are you sure?

---

## What the linter says, and why each one is wrong

**"Submit" and "OK" name the mechanism.** The user's goal is a render, not a form
submission. "OK" is worse: it forces the reader back up to the title to learn what they
just agreed to.

**"Ready to continue?" asks permission.** A button takes an action. A question invites
hesitation at the exact moment you want none.

**"Click here" says nothing about the destination** and is unusable by anyone navigating by
link list.

**The placeholder is being used as a label**, so it disappears on focus and takes the
user's only reference with it.

**"Oops! Something went wrong" names a feeling, not a cause.** No what, no why, no fix. The
user is left to guess whether to retry, resize, or give up.

**"Invalid request. Error occurred while the render was being processed by the server"**
fails four ways: it blames the input, it uses passive voice to hide the actor, it explains
the system's internals instead of the user's next step, and it offers no recovery.

**"You didn't save your work"** blames the reader for a system failure, then hedges the
consequence with "might potentially" and softens it with "unfortunately". At the one moment
the user needs certainty, the copy offers none.

**"No data" wastes the most attentive screen in the product.** The user is looking directly
at it and wants something to happen.

**"Are you sure?" names no consequence.** Sure about what, affecting how many things,
reversible or not?
