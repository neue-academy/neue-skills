# Section timing constants

Motion values that stay the same across pages. Load this file only when adding motion.

The governing rule: motion clarifies where something came from. Any animation that does
not answer "where did this come from" is decoration, and decoration in a hero costs
conversions because it delays the reader's first read.

---

## Easing curves

| Name | Value | Use for |
|---|---|---|
| Entrance | `cubic-bezier(0.22, 1, 0.36, 1)` | Elements arriving. Fast out, long settle |
| Exit | `cubic-bezier(0.4, 0, 1, 1)` | Elements leaving. Accelerate away, no settle |
| Hover / micro | `ease` at 180ms | Buttons, arrows, link underlines |
| Scroll-linked | `linear` | Anything driven by scroll position. Never ease a scrub |

Never use `ease-in-out` for entrances. It starts slow, which reads as lag.

## Durations

| Motion | Duration |
|---|---|
| Micro-interaction (hover, focus, arrow nudge) | `120–200ms` |
| Element entrance (fade + rise) | `550–650ms` |
| Section entrance | `700ms` maximum |
| Modal / overlay open | `280ms` |
| Anything the reader waits on | Never exceeds `700ms` |

Over 700ms, the reader has already moved their eyes and the motion is now behind them.

## Reveal delays (stagger)

Stagger builds reading order. It does not decorate.

| Position | Delay |
|---|---|
| Eyebrow | `0ms` |
| `h1` | `90ms` |
| Subhead | `180ms` |
| CTA + terms line | `270ms` |
| Each subsequent sibling | `+90ms`, capped at `360ms` total |

**Cap the total stagger at 360ms.** A hero whose CTA appears 900ms after load has a CTA
the reader never saw, because the first scroll happens sooner than that.

Reference implementation:

```css
@media (prefers-reduced-motion: no-preference) {
  @keyframes rise {
    from { opacity: 0; transform: translateY(14px); }
    to   { opacity: 1; transform: none; }
  }
  .rise { animation: rise 620ms cubic-bezier(0.22, 1, 0.36, 1) both; }
  .d1 { animation-delay: 90ms; }
  .d2 { animation-delay: 180ms; }
  .d3 { animation-delay: 270ms; }
}
```

## Transform distances

| Motion | Distance |
|---|---|
| Text rise | `14px` |
| Card rise | `20px` |
| Hover lift | `2px` |
| Arrow nudge | `3px` |
| Parallax range | `8%` of viewport height, maximum |

Rises over 40px read as a page that has not finished loading.

## Scroll-driven reveals

- Trigger at **20% of viewport height** from the bottom, so the element is already
  readable when it settles.
- Animate **once**. Elements that re-animate on scroll-up make the page feel unstable.
- Never scroll-reveal the `h1` or the primary CTA. Both are above the fold, and both
  must be readable at `t=0` even if scripts fail.
- Prefer CSS `animation-timeline: view()` where support allows, with an
  `@supports not (animation-timeline: view())` fallback that leaves elements visible.
  A reveal that fails must fail **visible**, never hidden.

## Reduced motion is not optional

Every animation lives inside `@media (prefers-reduced-motion: no-preference)`, so the
default state for a reader who has expressed a preference is no motion at all — not a
"reduced" version bolted on afterwards.

```css
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  * { animation: none !important; transition: none !important; }
}
```

`audit_page.py` blocks a page that animates without a `prefers-reduced-motion` rule.
Vestibular disorders affect a large minority of readers, and a reveal that triggers
nausea has cost you more than a conversion.

## Performance budget

| Metric | Budget |
|---|---|
| Animated properties | `transform` and `opacity` only |
| Frame rate target | 60fps on 5-year-old laptop hardware |
| Concurrent animations on load | 5 maximum |
| Layout-triggering animation | Zero. Never animate `width`, `height`, `top`, `margin` |

Animating anything other than `transform` and `opacity` forces layout or paint on every
frame. On the hardware your readers actually own, that is where the frames go.
