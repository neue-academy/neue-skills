---
name: conversion-architect
description: Assembles and audits high-converting landing pages — section order, CTA hierarchy, responsive layout, motion timing, accessibility — then deploys them to a live Vercel URL. Enforces a five-section contract (hero, proof, objections, offer, final-cta) and a single-primary-CTA rule with a structural auditor that blocks deploys on violations. Use when building, restructuring, auditing, or shipping a landing page, sales page, waitlist page, or squeeze page, and when a page needs to go live on Vercel.
---

# Conversion Architect

## Boundaries — read this first

This skill assembles pages. It does not write copy and it does not own deployment logic.

- **For copy generation and voice, invoke `copywriter-superhero`.** Do not write on-page
  copy from scratch here. Take the winning angle from that skill's output and place it.
- **For export and shipping, invoke `json-exporter`.** Do not handle export logic here.
  `scripts/deploy_to_vercel.sh` is the thin static-page path only.
- **Structure, hierarchy, layout, motion, accessibility, and the deploy gate are yours.**
  Nothing else.

Two skills doing the same job is the most common failure mode in a multi-skill repo,
because the agent picks between them inconsistently and you get different results on
identical requests. If you find yourself writing a headline here, stop and call
`copywriter-superhero`.

---

## The loop

```
Task Progress:
- [ ] 1. Get the copy (from copywriter-superhero, linted and passing)
- [ ] 2. Assemble the five sections in contract order
- [ ] 3. Enforce the CTA hierarchy
- [ ] 4. Run audit_page.py. Fix. Re-run until exit 0
- [ ] 5. Deploy, verify the live URL returns 200
```

## Step 1 — Get the copy first

Never assemble a page around placeholder text. Structure decisions depend on real
sentence lengths: a 6-word headline and a 16-word headline need different hero layouts.

Run `copywriter-superhero`, take its three angles, and pick one to build. If the user has
not chosen, build the **Logic** angle and say which one you used.

## Step 2 — Assemble the five sections, in order

Every page is exactly these five, in this order. The order is the argument: make the
claim, prove it, clear the objection, name the price, ask once.

```html
<main>
  <section data-section="hero">      <!-- one h1, one claim, one CTA -->
  <section data-section="proof">     <!-- figures + one attributed result -->
  <section data-section="objections"><!-- the three real reasons people don't buy -->
  <section data-section="offer">     <!-- price, terms, what arrives. No CTA -->
  <section data-section="final-cta"> <!-- the same ask, friction removed -->
</main>
```

The `data-section` attributes are not decoration. `scripts/audit_page.py` reads them to
verify order and completeness, so a page without them cannot be audited or deployed.

What each section **is**, element by element, plus spacing and type
scale: [references/conversion-anatomy.md](references/conversion-anatomy.md).

**Adding a sixth section is how pages get worse.** Every extra section is another thing
competing with the CTA. If the user asks for a features grid, a comparison table, or an
FAQ, fold it into `proof` or `objections`. The auditor warns past two extras.

## Step 3 — Enforce the CTA hierarchy

Hard rules, all mechanically checked:

- **One `h1`.** Under 14 words. One claim, never two joined by "and".
- **One subhead.** It carries the number or the mechanism the `h1` asserted.
- **One primary CTA, repeated at most twice** — hero and `final-cta`. Nowhere else.
- **Identical label both times**, word for word. A different label reads as a different
  offer.
- **Zero competing CTAs.** At most one low-emphasis secondary link, never in the hero.
- **Imperative CTAs only.** Verb + object.

Mark them so the audit can see them:

```html
<a href="#claim" data-cta="primary">Lock the founding rate</a>
<a href="#week-one" data-cta="secondary">See what lands in week one</a>
```

**The named failure:** *two CTAs above the fold splits intent and measurably drops
conversion.* A reader who must choose between two actions frequently chooses neither.
This is the rule most often broken by "just add a Learn More button", and the auditor
blocks it rather than trusting anyone to remember.

A question CTA ("Ready to get started?") asks permission. It is blocked, not warned.

## Step 4 — Audit until it passes

```bash
python3 skills/conversion-architect/scripts/audit_page.py page.html
```

Checks section order and completeness, `h1` count and length, heading-level skips, CTA
count/consistency/form, hero CTA count, `<title>`, meta description, viewport, `lang`,
Open Graph, `img` alt text, `prefers-reduced-motion`, focus styles, stripped outlines,
form labels, and `rel="noopener"`.

- **BLOCK** findings must all be fixed. The deploy script refuses to ship past them.
- **WARN** findings must be fixed or justified in one line.
- Exit `0` passes. `--json` for programmatic use.

The auditor cannot see contrast, keyboard order, or 320px reflow. Before deploying, run
the four manual checks at the bottom of
[references/accessibility-checklist.md](references/accessibility-checklist.md).

### Motion

Add motion only after the page passes without it. Every animation lives inside
`@media (prefers-reduced-motion: no-preference)`, animates `transform` and `opacity`
only, and caps total hero stagger at 360ms. Never scroll-reveal the `h1` or the primary
CTA — a reveal that fails must fail visible.

All values: [references/section-timing-constants.md](references/section-timing-constants.md).

## Step 5 — Deploy and verify

```bash
export VERCEL_TOKEN=...   # or put it in .env.local, never in a committed file
./skills/conversion-architect/scripts/deploy_to_vercel.sh page.html --project neue-landing
```

The script stages the page, **runs the audit and refuses to deploy a failing page**,
deploys to production, then polls the live URL until it returns 200 before reporting
success. It redacts tokens from any error output.

Flags: `--preview` for a non-production deploy, `--project NAME` to target a Vercel
project, `--scope TEAM` for a team account, `--skip-audit` to override the gate (record
why in your handover).

**Token handling:** read from `$VERCEL_TOKEN`, then `.env.local`, then `.env`, then a
local `vercel login` session. Never hard-code a token into a script and never commit
one. `.env*` is gitignored in this repo.

**Not done until it runs clean twice.** A page that deploys once may have picked up a
warm cache or an already-linked project. Deploy, verify 200, then deploy again.

---

## Reference index

| File | Read it when |
|---|---|
| [references/conversion-anatomy.md](references/conversion-anatomy.md) | Assembling sections, or picking spacing and type values |
| [references/section-timing-constants.md](references/section-timing-constants.md) | Adding any motion |
| [references/accessibility-checklist.md](references/accessibility-checklist.md) | Before every deploy |
| [examples/reference-page.html](examples/reference-page.html) | A working page that passes the audit with zero findings |

`examples/reference-page.html` is the canonical implementation: five sections in order,
two identical primary CTAs, fluid type scale, staggered hero, reduced-motion fallback,
labelled form field, and visible focus rings. Start from it rather than from a blank
file.
