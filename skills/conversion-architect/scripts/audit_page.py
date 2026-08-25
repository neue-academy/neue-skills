#!/usr/bin/env python3
"""Audit a landing page against the section-anatomy contract.

Turns the rules in SKILL.md into a gate. Structure, CTA hierarchy, heading order and
accessibility are all mechanically checkable, so they should never be left to
inspection.

Usage:
    python3 audit_page.py page.html
    python3 audit_page.py page.html --json

Exit codes:
    0  PASS — zero BLOCK findings
    1  FAIL
    2  usage error

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from html.parser import HTMLParser
from typing import Dict, List, Optional, Tuple

REQUIRED_SECTIONS = ["hero", "proof", "objections", "offer", "final-cta"]
IMPERATIVE_VERBS = set(
    """get build ship start join claim lock open read watch download copy grab
    install book reserve save switch take stop see try test deploy secure
    unlock-me pick keep add send drop hit fix study steal""".split()
)
MAX_H1_WORDS = 14
MAX_PRIMARY_CTAS = 2


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.html_attrs: Dict[str, str] = {}
        self.title = ""
        self.metas: List[Dict[str, str]] = []
        self.sections: List[Tuple[str, int]] = []
        self.headings: List[Tuple[str, str, int]] = []
        self.images: List[Tuple[Dict[str, str], int]] = []
        self.links: List[Tuple[Dict[str, str], str, int]] = []
        self.buttons: List[Tuple[Dict[str, str], str, int]] = []
        self.inputs: List[Tuple[Dict[str, str], int]] = []
        self.labels: List[Dict[str, str]] = []
        self.style_blocks: List[str] = []
        self._stack: List[Tuple[str, Dict[str, str], int]] = []
        self._capture: Optional[str] = None
        self._buffer = ""

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        attr = {k.lower(): (v or "") for k, v in attrs}
        line = self.getpos()[0]
        if tag == "html":
            self.html_attrs = attr
        elif tag == "meta":
            self.metas.append(attr)
        elif tag == "img":
            self.images.append((attr, line))
        elif tag in ("input", "textarea", "select"):
            self.inputs.append((attr, line))
        elif tag == "label":
            self.labels.append(attr)
        elif tag == "section" and attr.get("data-section"):
            self.sections.append((attr["data-section"].strip().lower(), line))

        if tag in ("title", "h1", "h2", "h3", "h4", "a", "button", "style"):
            self._capture = tag
            self._buffer = ""
            self._stack.append((tag, attr, line))

    def handle_endtag(self, tag: str) -> None:
        if self._capture == tag and self._stack:
            open_tag, attr, line = self._stack.pop()
            text = re.sub(r"\s+", " ", self._buffer).strip()
            if open_tag == "title":
                self.title = text
            elif open_tag in ("h1", "h2", "h3", "h4"):
                self.headings.append((open_tag, text, line))
            elif open_tag == "a":
                self.links.append((attr, text, line))
            elif open_tag == "button":
                self.buttons.append((attr, text, line))
            elif open_tag == "style":
                self.style_blocks.append(self._buffer)
            self._capture = None
            self._buffer = ""

    def handle_data(self, data: str) -> None:
        if self._capture:
            self._buffer += data


class Finding:
    def __init__(self, check: str, severity: str, message: str,
                 line: Optional[int] = None, fix: str = "") -> None:
        self.check = check
        self.severity = severity
        self.message = message
        self.line = line
        self.fix = fix

    def as_dict(self) -> Dict[str, object]:
        return {
            "check": self.check,
            "severity": self.severity,
            "line": self.line,
            "message": self.message,
            "fix": self.fix,
        }


def meta_content(parser: PageParser, name: str) -> Optional[str]:
    for meta in parser.metas:
        if meta.get("name", "").lower() == name:
            return meta.get("content", "")
    return None


def audit(html: str) -> Dict[str, object]:
    parser = PageParser()
    parser.feed(html)
    findings: List[Finding] = []
    css = "\n".join(parser.style_blocks) + "\n" + html

    def block(check: str, message: str, fix: str, line: Optional[int] = None) -> None:
        findings.append(Finding(check, "BLOCK", message, line, fix))

    def warn(check: str, message: str, fix: str, line: Optional[int] = None) -> None:
        findings.append(Finding(check, "WARN", message, line, fix))

    # --- section anatomy -------------------------------------------------------------
    found = [name for name, _line in parser.sections]
    missing = [s for s in REQUIRED_SECTIONS if s not in found]
    if missing:
        block(
            "section-missing",
            "missing required section(s): %s" % ", ".join(missing),
            'Every page carries all five: hero, proof, objections, offer, final-cta. '
            'Mark each with <section data-section="...">.',
        )
    ordered = [s for s in found if s in REQUIRED_SECTIONS]
    expected_order = [s for s in REQUIRED_SECTIONS if s in ordered]
    if ordered != expected_order:
        block(
            "section-order",
            "section order is %s, contract requires %s"
            % (" > ".join(ordered), " > ".join(expected_order)),
            "Reorder the sections. The order is the argument: claim, then proof, then "
            "objection, then price, then ask.",
        )
    extras = [s for s in found if s not in REQUIRED_SECTIONS]
    if len(extras) > 2:
        warn(
            "section-extra",
            "%d sections outside the contract: %s" % (len(extras), ", ".join(extras)),
            "Each extra section is another thing competing with the CTA. Fold them into "
            "proof or objections, or delete them.",
        )

    # --- heading hierarchy -----------------------------------------------------------
    h1s = [h for h in parser.headings if h[0] == "h1"]
    if len(h1s) != 1:
        block(
            "h1-count",
            "%d <h1> elements found, contract requires exactly 1" % len(h1s),
            "One page, one claim, one h1. Demote the others to h2.",
            h1s[1][2] if len(h1s) > 1 else None,
        )
    elif len(h1s[0][1].split()) > MAX_H1_WORDS:
        warn(
            "h1-length",
            "h1 is %d words (max %d)" % (len(h1s[0][1].split()), MAX_H1_WORDS),
            "A headline the reader cannot finish in one glance is a paragraph.",
            h1s[0][2],
        )
    levels = [int(h[0][1]) for h in parser.headings]
    for index in range(1, len(levels)):
        if levels[index] - levels[index - 1] > 1:
            warn(
                "heading-skip",
                "heading level jumps from h%d to h%d"
                % (levels[index - 1], levels[index]),
                "Screen-reader users navigate by heading level. Do not skip one.",
                parser.headings[index][2],
            )
            break

    # --- CTA hierarchy ---------------------------------------------------------------
    clickables = [(a, t, l) for a, t, l in parser.links + parser.buttons]
    primary = [(a, t, l) for a, t, l in clickables
               if a.get("data-cta", "").lower() == "primary"]
    secondary = [(a, t, l) for a, t, l in clickables
                 if a.get("data-cta", "").lower() == "secondary"]
    if not primary:
        block(
            "cta-missing",
            'no element marked data-cta="primary"',
            'Mark the primary action data-cta="primary" so the hierarchy is auditable, '
            "not just visual.",
        )
    elif len(primary) > MAX_PRIMARY_CTAS:
        block(
            "cta-count",
            "%d primary CTAs found (max %d)" % (len(primary), MAX_PRIMARY_CTAS),
            "Two CTAs above the fold splits intent and measurably drops conversion. "
            "Primary CTA appears in the hero and in final-cta. Nowhere else.",
            primary[MAX_PRIMARY_CTAS][2],
        )
    if len(secondary) > 1:
        warn(
            "cta-secondary",
            "%d secondary CTAs found (max 1)" % len(secondary),
            "One escape hatch is a courtesy. Two is a menu.",
            secondary[1][2],
        )
    primary_texts = {t.lower() for _a, t, _l in primary if t}
    if len(primary_texts) > 1:
        block(
            "cta-inconsistent",
            "primary CTA label differs across the page: %s"
            % "; ".join('"%s"' % t for t in sorted(primary_texts)),
            "Repeat the same words. A different label reads as a different offer.",
        )
    for attrs, text, line in primary:
        first = re.sub(r"[^a-z]", "", text.split()[0].lower()) if text.split() else ""
        if text.endswith("?"):
            block(
                "cta-question",
                'primary CTA "%s" is a question' % text,
                "A question CTA asks permission. Use verb + object: "
                '"Claim the founding rate".',
                line,
            )
        elif first and first not in IMPERATIVE_VERBS:
            warn(
                "cta-verb",
                'primary CTA "%s" does not open with an imperative verb' % text,
                "Verb first, object second.",
                line,
            )
        if not attrs.get("href") and not attrs.get("type"):
            warn("cta-target", 'primary CTA "%s" has no href or type' % text,
                 "A CTA that goes nowhere is decoration.", line)

    hero_line = next((l for n, l in parser.sections if n == "hero"), None)
    proof_line = next((l for n, l in parser.sections if n == "proof"), None)
    if hero_line is not None and proof_line is not None:
        in_hero = [
            (a, t, l) for a, t, l in clickables
            if hero_line <= l < proof_line
            and (a.get("data-cta") or re.search(r"\bbtn|button|cta\b",
                                                a.get("class", ""), re.IGNORECASE))
        ]
        if len(in_hero) > 1:
            block(
                "hero-cta-count",
                "%d CTAs inside the hero (max 1)" % len(in_hero),
                "One ask above the fold. Move the rest below proof.",
                in_hero[1][2],
            )

    # --- metadata --------------------------------------------------------------------
    if not parser.title:
        block("title-missing", "no <title>", "Add a title. It is the SEO headline and "
              "the browser-tab label.")
    elif not 15 <= len(parser.title) <= 65:
        warn("title-length", "<title> is %d characters (aim 15–65)" % len(parser.title),
             "Under 15 says nothing; over 65 truncates in search results.")
    description = meta_content(parser, "description")
    if description is None:
        block("meta-description", "no meta description",
              "Add one, 50–160 characters. It is the only copy you control in search "
              "results.")
    elif not 50 <= len(description) <= 160:
        warn("meta-description-length",
             "meta description is %d characters (aim 50–160)" % len(description),
             "Rewrite to fit the snippet window.")
    if not any(m.get("name", "").lower() == "viewport" for m in parser.metas):
        block("viewport", "no viewport meta tag",
              'Add <meta name="viewport" content="width=device-width, initial-scale=1">'
              " or the page renders zoomed out on every phone.")
    if not parser.html_attrs.get("lang"):
        block("lang", "<html> has no lang attribute",
              'Add lang="en". Screen readers pick pronunciation from it.')
    if not re.search(r'property=["\']og:', html, re.IGNORECASE):
        warn("open-graph", "no Open Graph tags",
             "Add og:title, og:description and og:image, or shared links render blank.")

    # --- accessibility ---------------------------------------------------------------
    for attrs, line in parser.images:
        if "alt" not in attrs:
            block("img-alt", "<img> has no alt attribute",
                  'Add alt text, or alt="" if the image is decorative.', line)
    animated = re.search(r"(animation|transition|@keyframes|scroll-timeline)", css,
                         re.IGNORECASE)
    if animated and not re.search(r"prefers-reduced-motion", css, re.IGNORECASE):
        block("reduced-motion", "the page animates but has no prefers-reduced-motion "
              "fallback",
              "Wrap motion in @media (prefers-reduced-motion: no-preference), or disable "
              "it in @media (prefers-reduced-motion: reduce). Vestibular disorders are "
              "not an edge case.")
    if not re.search(r":focus-visible|:focus\b", css):
        block("focus-state", "no focus styles found",
              "Add a visible :focus-visible outline. Keyboard users cannot see a hover "
              "state.")
    if re.search(r"outline\s*:\s*(none|0)", css) and not re.search(
        r":focus-visible[^{]*\{[^}]*outline", css
    ):
        block("focus-removed", "outline is removed without a :focus-visible replacement",
              "Never strip the outline without providing another visible focus indicator.")
    labelled = {l.get("for", "") for l in parser.labels}
    for attrs, line in parser.inputs:
        if attrs.get("type", "").lower() in ("hidden", "submit", "button"):
            continue
        has_label = (
            attrs.get("id", "") in labelled
            or attrs.get("aria-label")
            or attrs.get("aria-labelledby")
        )
        if not has_label:
            block("input-label", "form field has no label or aria-label",
                  "Every field needs a programmatic label. Placeholder text is not a "
                  "label — it disappears on focus.", line)
    for attrs, text, line in parser.links:
        href = attrs.get("href", "")
        if attrs.get("target") == "_blank" and "noopener" not in attrs.get("rel", ""):
            warn("link-rel", 'target="_blank" without rel="noopener"',
                 'Add rel="noopener" to prevent the opened page reaching window.opener.',
                 line)
        if href and not text and not attrs.get("aria-label"):
            warn("link-name", "link has no accessible name",
                 "Add link text or an aria-label.", line)

    # --- scoring ---------------------------------------------------------------------
    blocking = [f for f in findings if f.severity == "BLOCK"]
    return {
        "passed": not blocking,
        "sections": found,
        "primary_ctas": len(primary),
        "findings": [f.as_dict() for f in findings],
        "block_count": len(blocking),
        "warn_count": len(findings) - len(blocking),
    }


def report(result: Dict[str, object], source: str) -> None:
    print("PAGE AUDIT — %s" % source)
    print("sections: %s" % (" > ".join(result["sections"]) or "none marked"))
    print("primary CTAs: %d" % result["primary_ctas"])
    print("")
    for severity in ("BLOCK", "WARN"):
        group = [f for f in result["findings"] if f["severity"] == severity]
        if not group:
            continue
        label = ("BLOCK — must fix before deploy" if severity == "BLOCK"
                 else "WARN — fix unless you can justify it")
        print("%s (%d)" % (label, len(group)))
        group.sort(key=lambda f: (f["line"] is None, f["line"] or 0))
        for finding in group:
            location = "%-6s" % ("L%d" % finding["line"] if finding["line"] else "--")
            print("  %s %s" % (location, finding["message"]))
            if finding["fix"]:
                print("        fix: %s" % finding["fix"])
        print("")
    verdict = "PASS" if result["passed"] else "FAIL"
    print("VERDICT %s — %d block, %d warn"
          % (verdict, result["block_count"], result["warn_count"]))
    if not result["passed"]:
        print("NEXT: fix every BLOCK finding, then re-run. Do not deploy a failing page.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("page", help="path to the HTML file, or - for stdin")
    parser.add_argument("--json", dest="as_json", action="store_true")
    args = parser.parse_args()

    if args.page == "-":
        html = sys.stdin.read()
        source = "<stdin>"
    else:
        if not os.path.isfile(args.page):
            print("error: no such file: %s" % args.page, file=sys.stderr)
            return 2
        with open(args.page, "r", encoding="utf-8") as handle:
            html = handle.read()
        source = args.page

    result = audit(html)
    if args.as_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        report(result, source)
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
