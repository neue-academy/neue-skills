#!/usr/bin/env python3
"""Export a page spec plus linted copy into a deployable static bundle.

This is the seam between writing and shipping. Copy comes from copywriter-superhero as
markdown angles, structure comes from a page spec JSON, and this produces the artefacts
that conversion-architect's deploy script sends to Vercel.

Usage:
    python3 export.py --spec page.json --copy draft.md --angle logic --out dist/
    python3 export.py --spec page.json --validate-only

Writes: dist/index.html, dist/og.svg, dist/manifest.json

Exit codes:
    0  bundle written
    2  spec or copy invalid — nothing written

Standard library only.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import string
import sys
from typing import Dict, List, Optional, Tuple

REQUIRED_ANGLE_FIELDS = ("headline", "subhead", "body", "cta")

CSS = """
  :root {
    --ink: #08090a; --ink-2: #101214; --line: #22262b;
    --fg: #f4f5f6; --fg-dim: #9aa3ab; --accent: $ACCENT;
    --radius: 14px; --measure: 62ch;
    --step: clamp(1rem, 0.6rem + 1.4vw, 1.4rem);
  }
  *, *::before, *::after { box-sizing: border-box; }
  html { -webkit-text-size-adjust: 100%; scroll-behavior: smooth; }
  body {
    margin: 0; background: var(--ink); color: var(--fg);
    font-family: ui-sans-serif, -apple-system, "Segoe UI", Inter, Helvetica, Arial, sans-serif;
    font-size: clamp(1rem, 0.95rem + 0.2vw, 1.075rem); line-height: 1.6;
    -webkit-font-smoothing: antialiased;
  }
  .mono {
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 0.72rem; letter-spacing: 0.14em; text-transform: uppercase; color: var(--fg-dim);
  }
  .wrap { width: 100%; max-width: 1080px; margin-inline: auto; padding-inline: clamp(1.25rem, 4vw, 3rem); }
  section { padding-block: clamp(4rem, 9vw, 7.5rem); border-top: 1px solid var(--line); }
  section:first-of-type { border-top: 0; }
  h1, h2, h3 { margin: 0; font-weight: 560; letter-spacing: -0.022em; line-height: 1.08; }
  h1 { font-size: clamp(2.6rem, 1.4rem + 5.4vw, 5.1rem); }
  h2 { font-size: clamp(1.85rem, 1.2rem + 2.2vw, 2.9rem); }
  h3 { font-size: 1.1rem; letter-spacing: -0.01em; line-height: 1.35; }
  p { margin: 0; max-width: var(--measure); }
  .lede { font-size: var(--step); color: var(--fg-dim); margin-top: 1.5rem; }
  .hero { padding-block: clamp(5rem, 12vw, 9.5rem); position: relative; overflow: hidden; }
  .hero::after {
    content: ""; position: absolute; inset: auto -20% -60% 30%; height: 420px;
    background: radial-gradient(closest-side, $GLOW, transparent 72%); pointer-events: none;
  }
  .hero .mono { display: block; margin-bottom: 2rem; }
  .hero-meta { margin-top: 1.25rem; font-size: 0.9rem; color: var(--fg-dim); }
  .action {
    display: inline-flex; align-items: center; gap: 0.6rem; margin-top: 2.5rem;
    padding: 0.95rem 1.6rem; background: var(--accent); color: #0b0d05;
    border: 1px solid var(--accent); border-radius: 999px; font: inherit; font-weight: 600;
    letter-spacing: -0.01em; text-decoration: none; cursor: pointer;
  }
  .action:hover { filter: brightness(1.08); }
  .action .arrow { transition: transform 180ms ease; }
  .action:hover .arrow { transform: translateX(3px); }
  .ghost {
    display: inline-block; margin-top: 1.5rem; color: var(--fg-dim); text-decoration: none;
    border-bottom: 1px solid var(--line); padding-bottom: 2px;
  }
  .ghost:hover { color: var(--fg); border-color: var(--fg-dim); }
  .figures {
    display: grid; gap: 1px; margin-top: 3rem; background: var(--line);
    border: 1px solid var(--line); border-radius: var(--radius); overflow: hidden;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  }
  .figure { background: var(--ink-2); padding: 1.75rem 1.5rem; }
  .figure b {
    display: block; font-size: clamp(2rem, 1.4rem + 1.8vw, 2.9rem); font-weight: 560;
    letter-spacing: -0.03em; line-height: 1;
  }
  .figure span { display: block; margin-top: 0.6rem; font-size: 0.86rem; color: var(--fg-dim); }
  blockquote {
    margin: 3rem 0 0; padding-left: 1.5rem; border-left: 2px solid var(--accent);
    max-width: 54ch; font-size: var(--step);
  }
  blockquote cite { display: block; margin-top: 0.9rem; font-size: 0.86rem; font-style: normal; color: var(--fg-dim); }
  .qa { display: grid; gap: 2.25rem; margin-top: 3rem; grid-template-columns: repeat(auto-fit, minmax(270px, 1fr)); }
  .qa p { margin-top: 0.7rem; color: var(--fg-dim); font-size: 0.97rem; }
  .card {
    margin-top: 3rem; padding: clamp(1.75rem, 4vw, 2.75rem); background: var(--ink-2);
    border: 1px solid var(--line); border-radius: var(--radius);
  }
  .price { display: flex; align-items: baseline; gap: 0.7rem; flex-wrap: wrap; }
  .price b { font-size: clamp(2.4rem, 1.6rem + 2.4vw, 3.4rem); font-weight: 560; letter-spacing: -0.03em; line-height: 1; }
  .price s { color: var(--fg-dim); }
  .includes { margin: 2rem 0 0; padding: 0; list-style: none; display: grid; gap: 0.85rem; }
  .includes li { position: relative; padding-left: 1.6rem; color: var(--fg-dim); }
  .includes li::before { content: "\\2192"; position: absolute; left: 0; color: var(--accent); }
  form { margin-top: 2.5rem; display: flex; gap: 0.75rem; flex-wrap: wrap; align-items: flex-end; }
  .field { display: flex; flex-direction: column; gap: 0.5rem; flex: 1 1 260px; }
  input[type="email"] {
    padding: 0.9rem 1rem; background: var(--ink-2); color: var(--fg);
    border: 1px solid var(--line); border-radius: 999px; font: inherit;
  }
  input[type="email"]::placeholder { color: #5d666e; }
  form .action { margin-top: 0; }
  .fine { margin-top: 1.5rem; font-size: 0.84rem; color: #6d767e; }
  footer { border-top: 1px solid var(--line); padding-block: 2.5rem; }
  footer p { font-size: 0.82rem; color: #6d767e; max-width: none; }
  :focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; border-radius: 4px; }
  @media (prefers-reduced-motion: no-preference) {
    @keyframes rise { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
    .rise { animation: rise 620ms cubic-bezier(0.22, 1, 0.36, 1) both; }
    .d1 { animation-delay: 90ms; } .d2 { animation-delay: 180ms; } .d3 { animation-delay: 270ms; }
  }
  @media (prefers-reduced-motion: reduce) {
    html { scroll-behavior: auto; }
    .action .arrow { transition: none; }
  }
"""

PAGE = string.Template("""<!doctype html>
<html lang="$LANG">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>$TITLE</title>
<meta name="description" content="$DESCRIPTION">
<meta property="og:type" content="website">
<meta property="og:title" content="$TITLE">
<meta property="og:description" content="$DESCRIPTION">
<meta property="og:image" content="/og.svg">
<meta property="og:url" content="$URL">
<meta name="theme-color" content="#08090a">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='7' fill='$FAVICON_FILL'/><text x='16' y='23' font-family='monospace' font-size='20' font-weight='700' text-anchor='middle' fill='%230b0d05'>N</text></svg>">
<style>$CSS</style>
</head>
<body>

<main>
  <section data-section="hero" class="hero">
    <div class="wrap">
      <span class="mono rise">$BRAND_EYEBROW</span>
      <h1 class="rise d1">$HERO_HEADLINE</h1>
      <p class="lede rise d2">$HERO_SUBHEAD</p>
      <a class="action rise d3" href="#claim" data-cta="primary">
        $CTA_LABEL <span class="arrow" aria-hidden="true">&#8594;</span>
      </a>
      <p class="hero-meta rise d3">$HERO_TERMS</p>
    </div>
  </section>

  <section data-section="proof">
    <div class="wrap">
      <span class="mono">$PROOF_EYEBROW</span>
      <h2>$PROOF_HEADING</h2>
      <div class="figures">
$FIGURES
      </div>
$QUOTE
    </div>
  </section>

  <section data-section="objections">
    <div class="wrap">
      <span class="mono">$OBJ_EYEBROW</span>
      <h2>$OBJ_HEADING</h2>
      <div class="qa">
$OBJECTIONS
      </div>
    </div>
  </section>

  <section data-section="offer">
    <div class="wrap">
      <span class="mono">$OFFER_EYEBROW</span>
      <h2>$OFFER_HEADING</h2>
      <div class="card">
        <div class="price">
          <b>$PRICE</b><span class="mono">$PRICE_UNIT</span>$COMPARE
        </div>
        <ul class="includes">
$INCLUDES
        </ul>
$SECONDARY
      </div>
    </div>
  </section>

  <section data-section="final-cta" id="claim">
    <div class="wrap">
      <span class="mono">$FINAL_EYEBROW</span>
      <h2>$FINAL_HEADING</h2>
      <p class="lede">$FINAL_LEDE</p>
      <form action="$FORM_ACTION" method="post">
        <div class="field">
          <label class="mono" for="email">$FORM_LABEL</label>
          <input id="email" name="email" type="email" autocomplete="email" required
                 placeholder="$FORM_PLACEHOLDER">
        </div>
        <button class="action" type="submit" data-cta="primary">
          $CTA_LABEL <span class="arrow" aria-hidden="true">&#8594;</span>
        </button>
      </form>
      <p class="fine">$FINAL_FINE</p>
    </div>
  </section>
</main>

<footer>
  <div class="wrap"><p>$FOOTER</p></div>
</footer>

</body>
</html>
""")

OG = string.Template("""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630" role="img" aria-label="$ALT">
  <rect width="1200" height="630" fill="#08090a"/>
  <circle cx="980" cy="560" r="300" fill="$ACCENT" opacity="0.14"/>
  <text x="80" y="120" font-family="ui-monospace, Menlo, monospace" font-size="22"
        letter-spacing="4" fill="#9aa3ab">$EYEBROW</text>
$LINES
  <text x="80" y="560" font-family="ui-monospace, Menlo, monospace" font-size="22"
        letter-spacing="3" fill="$ACCENT">$CTA</text>
</svg>
""")


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def fail(problems: List[str]) -> None:
    print("export: spec/copy invalid — nothing written", file=sys.stderr)
    for problem in problems:
        print("  - %s" % problem, file=sys.stderr)
    raise SystemExit(2)


def parse_angles(markdown: str) -> Dict[str, Dict[str, str]]:
    """Extract {angle: {headline, subhead, body, cta}} from a copy deliverable."""
    # Author notes are not copy, and a trailing comment would otherwise be swallowed
    # into the last field of the last angle.
    markdown = re.sub(r"<!--.*?-->", " ", markdown, flags=re.DOTALL)
    heading = re.compile(
        r"^#{1,6}\s*(?:angle\s*)?\d*\s*[\u2014\u2013:\-]?\s*"
        r"(logic|pain|social[\s\-]?proof)\b.*$",
        re.IGNORECASE | re.MULTILINE,
    )
    matches = list(heading.finditer(markdown))
    angles: Dict[str, Dict[str, str]] = {}
    for index, match in enumerate(matches):
        name = re.sub(r"[\s\-]+", " ", match.group(1).lower())
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        block = markdown[match.end():end]
        fields: Dict[str, str] = {}
        for field in REQUIRED_ANGLE_FIELDS:
            found = re.search(
                r"^#{2,6}\s*%s\s*$\n(.*?)(?=^#{2,6}\s|\Z)" % field,
                block, re.IGNORECASE | re.MULTILINE | re.DOTALL,
            )
            if found:
                # A horizontal rule ends a field but is not a heading, so it would
                # otherwise be swallowed into the last field of each angle.
                text = re.sub(
                    r"(?m)^\s*(?:-{3,}|\*{3,}|_{3,})\s*$", "\n", found.group(1)
                )
                text = re.sub(r"\s*\n\s*", " ", text).strip()
                fields[field] = re.sub(r"^[*_#>\s]+|[-*_\s]+$", "", text)
        angles[name] = fields
    return angles


def validate_spec(spec: Dict[str, object]) -> List[str]:
    problems: List[str] = []

    def need(path: str, value: object, test: bool, message: str) -> None:
        if not test:
            problems.append("%s: %s" % (path, message))

    meta = spec.get("meta", {}) or {}
    need("meta.title", meta.get("title"), bool(meta.get("title")), "required")
    if meta.get("title"):
        need("meta.title", meta["title"], 15 <= len(meta["title"]) <= 65,
             "is %d characters, aim 15-65" % len(meta["title"]))
    description = meta.get("description", "")
    need("meta.description", description, bool(description), "required")
    if description:
        need("meta.description", description, 50 <= len(description) <= 160,
             "is %d characters, aim 50-160" % len(description))

    proof = spec.get("proof", {}) or {}
    figures = proof.get("figures", []) or []
    need("proof.figures", figures, 3 <= len(figures) <= 4,
         "has %d entries, contract requires 3-4" % len(figures))
    for index, figure in enumerate(figures):
        need("proof.figures[%d]" % index, figure,
             bool(figure.get("value")) and bool(figure.get("label")),
             "needs both value and label — a number without its unit is noise")

    objections = (spec.get("objections", {}) or {}).get("items", []) or []
    need("objections.items", objections, len(objections) == 3,
         "has %d entries, contract requires exactly 3" % len(objections))
    for index, item in enumerate(objections):
        need("objections.items[%d]" % index, item,
             bool(item.get("q")) and bool(item.get("a")),
             "needs both q and a")

    offer = spec.get("offer", {}) or {}
    need("offer.price", offer.get("price"), bool(offer.get("price")), "required")
    includes = offer.get("includes", []) or []
    need("offer.includes", includes, 4 <= len(includes) <= 6,
         "has %d entries, contract requires 4-6" % len(includes))

    final = spec.get("final", {}) or {}
    need("final.heading", final.get("heading"), bool(final.get("heading")), "required")
    return problems


def render_og(spec: Dict[str, object], headline: str, cta: str) -> str:
    words, lines, current = headline.split(), [], ""
    for word in words:
        candidate = (current + " " + word).strip()
        if len(candidate) > 26 and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    lines = lines[:3]
    body = "\n".join(
        '  <text x="80" y="%d" font-family="ui-sans-serif, Helvetica, Arial, sans-serif" '
        'font-size="76" font-weight="600" fill="#f4f5f6">%s</text>'
        % (250 + index * 88, esc(line))
        for index, line in enumerate(lines)
    )
    return OG.substitute(
        ALT=esc(headline),
        ACCENT=esc((spec.get("theme", {}) or {}).get("accent", "#d8ff3e")),
        EYEBROW=esc((spec.get("brand", {}) or {}).get("eyebrow", "")),
        LINES=body,
        CTA=esc(cta),
    )


def render(spec: Dict[str, object], angle: Dict[str, str]) -> Tuple[str, str]:
    meta = spec.get("meta", {}) or {}
    brand = spec.get("brand", {}) or {}
    proof = spec.get("proof", {}) or {}
    objections = spec.get("objections", {}) or {}
    offer = spec.get("offer", {}) or {}
    final = spec.get("final", {}) or {}
    theme = spec.get("theme", {}) or {}
    form = final.get("form", {}) or {}

    accent = theme.get("accent", "#d8ff3e")
    figures = "\n".join(
        '        <div class="figure"><b>%s</b><span>%s</span></div>'
        % (esc(f["value"]), esc(f["label"]))
        for f in proof.get("figures", [])
    )
    quote_data = proof.get("quote") or {}
    quote = ""
    if quote_data.get("text"):
        quote = (
            '      <blockquote>%s\n        <cite>%s</cite>\n      </blockquote>'
            % (esc(quote_data["text"]), esc(quote_data.get("cite", "")))
        )
    objection_blocks = "\n".join(
        "        <div>\n          <h3>%s</h3>\n          <p>%s</p>\n        </div>"
        % (esc(item["q"]), esc(item["a"]))
        for item in objections.get("items", [])
    )
    includes = "\n".join(
        "          <li>%s</li>" % esc(item) for item in offer.get("includes", [])
    )
    compare = ("<s>%s</s>" % esc(offer["compare"])) if offer.get("compare") else ""
    secondary_data = offer.get("secondary_cta") or {}
    secondary = ""
    if secondary_data.get("label"):
        secondary = (
            '        <a class="ghost" href="%s" data-cta="secondary">%s</a>'
            % (esc(secondary_data.get("href", "#claim")), esc(secondary_data["label"]))
        )

    page = PAGE.substitute(
        LANG=esc(meta.get("lang", "en")),
        TITLE=esc(meta.get("title", "")),
        DESCRIPTION=esc(meta.get("description", "")),
        URL=esc(meta.get("url", "")),
        FAVICON_FILL=accent.replace("#", "%23"),
        CSS=string.Template(CSS).substitute(
            ACCENT=accent,
            GLOW=theme.get("glow", "rgba(216,255,62,0.14)"),
        ),
        BRAND_EYEBROW=esc(brand.get("eyebrow", "")),
        HERO_HEADLINE=esc(angle["headline"]),
        HERO_SUBHEAD=esc(angle["subhead"]),
        CTA_LABEL=esc(angle["cta"]),
        HERO_TERMS=esc((spec.get("hero", {}) or {}).get("terms", "")),
        PROOF_EYEBROW=esc(proof.get("eyebrow", "")),
        PROOF_HEADING=esc(proof.get("heading", "")),
        FIGURES=figures,
        QUOTE=quote,
        OBJ_EYEBROW=esc(objections.get("eyebrow", "")),
        OBJ_HEADING=esc(objections.get("heading", "")),
        OBJECTIONS=objection_blocks,
        OFFER_EYEBROW=esc(offer.get("eyebrow", "")),
        OFFER_HEADING=esc(offer.get("heading", "")),
        PRICE=esc(offer.get("price", "")),
        PRICE_UNIT=esc(offer.get("unit", "")),
        COMPARE=compare,
        INCLUDES=includes,
        SECONDARY=secondary,
        FINAL_EYEBROW=esc(final.get("eyebrow", "")),
        FINAL_HEADING=esc(final.get("heading", "")),
        FINAL_LEDE=esc(final.get("lede", "")),
        FORM_ACTION=esc(form.get("action", "#")),
        FORM_LABEL=esc(form.get("label", "Email address")),
        FORM_PLACEHOLDER=esc(form.get("placeholder", "you@example.com")),
        FINAL_FINE=esc(final.get("fine", "")),
        FOOTER=esc(brand.get("footer", "")),
    )
    return page, render_og(spec, angle["headline"], angle["cta"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, help="page spec JSON")
    parser.add_argument("--copy", help="copy deliverable markdown from copywriter-superhero")
    parser.add_argument("--angle", default="logic",
                        choices=("logic", "pain", "social proof"))
    parser.add_argument("--out", help="output directory for the bundle")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    if not os.path.isfile(args.spec):
        print("export: no such spec: %s" % args.spec, file=sys.stderr)
        return 2
    with open(args.spec, "r", encoding="utf-8") as handle:
        try:
            spec = json.load(handle)
        except ValueError as exc:
            print("export: spec is not valid JSON: %s" % exc, file=sys.stderr)
            return 2

    problems = validate_spec(spec)

    angle: Optional[Dict[str, str]] = None
    if args.copy:
        if not os.path.isfile(args.copy):
            print("export: no such copy file: %s" % args.copy, file=sys.stderr)
            return 2
        with open(args.copy, "r", encoding="utf-8") as handle:
            angles = parse_angles(handle.read())
        if args.angle not in angles:
            problems.append(
                'copy: no "%s" angle found. Present: %s. Run copywriter-superhero and '
                "keep its heading format." % (args.angle, ", ".join(angles) or "none")
            )
        else:
            angle = angles[args.angle]
            for field in REQUIRED_ANGLE_FIELDS:
                if not angle.get(field):
                    problems.append(
                        'copy: the "%s" angle has no ### %s block' % (args.angle, field)
                    )
    elif not args.validate_only:
        problems.append("--copy is required unless --validate-only is set")

    if problems:
        fail(problems)

    if args.validate_only:
        print("export: spec valid (%d figures, %d objections, %d includes)"
              % (len((spec.get("proof") or {}).get("figures", [])),
                 len((spec.get("objections") or {}).get("items", [])),
                 len((spec.get("offer") or {}).get("includes", []))))
        return 0

    if not args.out:
        print("export: --out is required", file=sys.stderr)
        return 2

    assert angle is not None
    page, og = render(spec, angle)
    os.makedirs(args.out, exist_ok=True)
    index_path = os.path.join(args.out, "index.html")
    with open(index_path, "w", encoding="utf-8") as handle:
        handle.write(page)
    with open(os.path.join(args.out, "og.svg"), "w", encoding="utf-8") as handle:
        handle.write(og)
    manifest = {
        "source_spec": os.path.relpath(args.spec),
        "source_copy": os.path.relpath(args.copy) if args.copy else None,
        "angle": args.angle,
        "headline": angle["headline"],
        "cta": angle["cta"],
        "bytes": len(page.encode("utf-8")),
        "artefacts": ["index.html", "og.svg"],
    }
    with open(os.path.join(args.out, "manifest.json"), "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    print("export: wrote %s (%d bytes), og.svg, manifest.json"
          % (index_path, manifest["bytes"]))
    print('export: angle "%s" — "%s"' % (args.angle, angle["headline"]))
    print("export: next — audit it, then deploy:")
    print("  python3 skills/conversion-architect/scripts/audit_page.py %s" % index_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
