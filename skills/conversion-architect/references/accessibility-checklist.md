# Accessibility checklist

`scripts/audit_page.py` enforces the mechanical half of this list. The rest needs a
human or a browser. Items marked **[auto]** are checked by the auditor; items marked
**[manual]** are on you.

An inaccessible landing page is also a leaking landing page: keyboard traps, invisible
focus and unlabelled fields cost conversions from people who were ready to buy.

---

## Structure

- **[auto]** Exactly one `h1` per page.
- **[auto]** Heading levels never skip (no `h1` → `h3`).
- **[auto]** `<html lang="en">` present. Screen readers pick pronunciation from it.
- **[manual]** Content sits inside `<main>`, with `<header>`/`<footer>` outside it.
- **[manual]** Reading order in the DOM matches visual order. CSS `order` and
  `grid-row` can silently scramble it for keyboard and screen-reader users.
- **[manual]** A skip link is the first focusable element on pages with navigation.

## Keyboard

- **[auto]** Focus styles exist.
- **[auto]** `outline: none` is never used without a `:focus-visible` replacement.
- **[manual]** Tab through the whole page. Every interactive element is reachable, in a
  sensible order, and the focus ring is visible against its own background.
- **[manual]** Focus ring uses `:focus-visible`, not `:focus`, so mouse clicks do not
  leave rings behind.
- **[manual]** No keyboard trap. `Tab` and `Shift+Tab` always escape.
- **[manual]** `Escape` closes any overlay, and focus returns to the trigger.
- **[manual]** Custom controls respond to `Enter` and `Space`. This is why a real
  `<button>` beats a `<div onclick>` every time.

## Forms

- **[auto]** Every field has a `<label for>`, `aria-label`, or `aria-labelledby`.
- **[manual]** Placeholder text is never the only label. It disappears on focus, which
  is exactly when the reader needs it.
- **[manual]** `type` and `autocomplete` are correct (`type="email"`,
  `autocomplete="email"`). Wrong `type` means the wrong mobile keyboard.
- **[manual]** Errors are announced, not only coloured: `aria-live="polite"` region, or
  `aria-invalid` plus `aria-describedby` on the field.
- **[manual]** Error text names the fix, not the failure. "Add the @ in your address",
  not "Invalid input".
- **[manual]** Required fields are marked in text, not by colour or an asterisk alone.
- **[manual]** Tap targets are at least 44×44px.

## Images and media

- **[auto]** Every `<img>` has an `alt` attribute.
- **[manual]** `alt` describes the **function**, not the file. Decorative images get
  `alt=""`, never a filename.
- **[manual]** Text baked into an image is repeated in real text. Screen readers,
  translation and search cannot read pixels.
- **[manual]** No autoplaying audio. Video that autoplays is muted and has a pause
  control.
- **[manual]** Video has captions.

## Motion

- **[auto]** Any animating page has a `prefers-reduced-motion` rule.
- **[manual]** Motion is wrapped in `@media (prefers-reduced-motion: no-preference)`, so
  no-motion is the default for readers who asked for it.
- **[manual]** Nothing flashes more than three times per second.
- **[manual]** Scroll-hijacking and reveal animations fail **visible**. If a script does
  not run, content is still readable.
- **[manual]** Parallax stays under 8% of viewport height.

## Colour and contrast

- **[manual]** Body text at 4.5:1 or better. Large text (24px+, or 19px+ bold) at 3:1.
- **[manual]** Dimmed secondary text is the usual failure. Measure it; a grey that looks
  fine on your monitor often lands near 3:1.
- **[manual]** Focus indicators at 3:1 against their adjacent background.
- **[manual]** Nothing is communicated by colour alone: error states, required fields,
  selected states, chart series.
- **[manual]** Check in both light and dark scheme if the page responds to
  `prefers-color-scheme`.

## Metadata and links

- **[auto]** `<title>`, meta description, and viewport meta all present.
- **[auto]** `target="_blank"` carries `rel="noopener"`.
- **[auto]** Every link has an accessible name.
- **[manual]** Link text makes sense out of context. Screen-reader users list links in
  isolation, so "here" and "read more" are useless.
- **[manual]** The CTA's accessible name matches its visible label. Decorative arrows
  inside a button carry `aria-hidden="true"`.

## Zoom and reflow

- **[manual]** At 200% browser zoom, nothing is clipped and nothing overlaps.
- **[manual]** At 320px viewport width there is no horizontal scroll.
- **[manual]** Body text is at least 16px on mobile. iOS Safari zooms the viewport on
  focus for anything smaller, which breaks the layout mid-form.

---

## Verifying

```bash
python3 skills/conversion-architect/scripts/audit_page.py page.html
```

Then, before every deploy, the four manual checks that catch the most real damage:

1. Tab through the page with the trackpad untouched.
2. Load it at 320px wide.
3. Turn on Reduce Motion in the OS and reload.
4. Measure the contrast of the dimmest text on the page.

Skipping these is how a page that "passes the audit" still fails a real reader.
