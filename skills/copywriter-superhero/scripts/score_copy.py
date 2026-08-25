#!/usr/bin/env python3
"""Score a copy draft against its regime's discipline, and optionally a brand voice.

A deterministic critic. It replaces "try to write well" with a gate that either passes
or names the exact line to fix, so the agent can iterate without a human in the loop.

Which rules apply depends on the regime, because a 3-word button and a 4,000-word sales
letter share almost no standards:

    microcopy   buttons, errors, empty states, tooltips, labels
    short-form  ads, headlines, hero sections, social, short emails
    long-form   sales pages, VSL scripts, long email sequences
    editorial   books, scripts, essays, newsletters, documentation prose
    functional  terms, policies, contracts, transactional email, help articles

Usage:
    python3 score_copy.py draft.md --regime short-form
    python3 score_copy.py draft.md --regime microcopy
    python3 score_copy.py letter.md --regime long-form --codex references/voice-codex-acme.json
    python3 score_copy.py draft.md --regime short-form --variants 1
    python3 score_copy.py - < draft.md --json

Brand voice is optional. With no --codex the linter uses plain-language defaults, so the
skill works with zero brand input and sharpens when a codex is supplied.

Exit codes:
    0  PASS — zero BLOCK findings and score >= the regime's minimum
    1  FAIL — fix the findings and re-run
    2  usage / config error

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import sys
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rules import Rules, load_many  # noqa: E402
from textstats import (  # noqa: E402
    BASE_VERB_OPENERS,
    HEDGES,
    LY_ADVERB,
    PASSIVE_HINT,
    SPEC_TOKEN,
    STOPWORDS,
    blank_comments,
    content_words,
    drop_headings,
    flesch_kincaid_grade,
    line_of,
    nominalizations,
    per_hundred,
    per_thousand,
    split_sentences,
    strip_markup,
    words_of,
)

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFERENCES = os.path.join(SKILL_DIR, "references")
DEFAULT_PROFILES = os.path.join(REFERENCES, "profiles.json")
DEFAULT_CODEX = os.path.join(REFERENCES, "voice-codex-default.json")
DEFAULT_TABLE = os.path.join(REFERENCES, "buzzword-replacement-table.md")

# Style gates a brand codex is allowed to override, and only where voice_governs.
VOICE_GATE_KEYS = (
    "max_mean_sentence_words",
    "min_sentence_words_cv",
    "min_short_sentence_ratio",
    "min_spec_tokens_per_100",
    "max_hedges_per_100",
    "max_ly_adverbs_per_100",
    "max_em_dash_per_1000",
    "max_passive_hint_per_100",
)

PENALTY = {
    "banned-word": 6,
    "banned-word-soft": 2,
    "banned-construction": 8,
    "protected-overuse": 3,
    "sentence-length": 8,
    "flat-rhythm": 10,
    "no-short-sentences": 5,
    "low-specificity": 10,
    "hedging": 4,
    "adverbs": 4,
    "em-dash": 4,
    "passive": 5,
    "nominalization": 5,
    "reading-grade": 8,
    "missing-angle": 12,
    "angle-overlap": 10,
    "duplicate-line": 8,
    "repeated-opener": 4,
    "no-imperative-cta": 5,
    "capitalization": 2,
    "exclamation": 3,
    "missing-triage": 6,
    "missing-section": 10,
    "microcopy-item": 8,
}
CATEGORY_CAP = 24

ANGLE_HEADING = re.compile(
    r"^#{1,6}\s*(?:angle\s*)?(\d+)?\s*[\u2014\u2013:\-]?\s*"
    r"(logic|pain|social[\s\-]?proof|proof|status|curiosity|contrarian)\b.*$",
    re.IGNORECASE | re.MULTILINE,
)
HEADING_LINE = re.compile(r"^(#{1,6})\s*(.+?)\s*$", re.MULTILINE)
CLAUSE_NUMBER = re.compile(r"^\**\d+\.\d+\**\s", re.MULTILINE)
# Well-written functional copy has no legalese, so detection cannot rely on legalese
# alone. Document furniture — clause numbers, retention periods, changelog headings —
# is the more reliable signal.
FUNCTIONAL_CUE = re.compile(
    r"\b(shall|hereby|herein|thereof|pursuant to|terms of service|privacy policy|"
    r"this agreement|the parties|liability|indemnif\w+|warrant\w+|governing law|"
    r"arbitration|effective date|data retention|retention period|release notes|"
    r"changelog|breaking change|deprecat\w+|unsubscribe|processor|business day|"
    r"we delete|migration guide)\b",
    re.IGNORECASE,
)


class Finding:
    def __init__(self, check: str, severity: str, message: str,
                 line: Optional[int] = None, evidence: str = "", fix: str = "") -> None:
        self.check = check
        self.severity = severity
        self.message = message
        self.line = line
        self.evidence = evidence
        self.fix = fix

    def as_dict(self) -> Dict[str, object]:
        return {
            "check": self.check,
            "severity": self.severity,
            "line": self.line,
            "message": self.message,
            "evidence": self.evidence,
            "fix": self.fix,
        }


# --- loading ------------------------------------------------------------------------


def load_json(path: str, what: str) -> Dict[str, object]:
    if not os.path.isfile(path):
        raise SystemExit("error: no %s at %s" % (what, path))
    with open(path, "r", encoding="utf-8") as handle:
        try:
            return json.load(handle)
        except ValueError as exc:
            raise SystemExit("error: %s is not valid JSON: %s" % (path, exc))


def resolve_profile(profiles: Dict[str, object], regime: str) -> Dict[str, object]:
    available = profiles.get("profiles", {})
    if regime not in available:
        raise SystemExit(
            "error: unknown regime %r. Available: %s"
            % (regime, ", ".join(sorted(available)))
        )
    return available[regime]


def microcopy_items(raw: str, kinds: Dict[str, object],
                    require_context: bool = False) -> List[Dict[str, object]]:
    """Find labelled strings written as "### Button — save draft".

    A body runs to the next heading of any level, so prose that follows the last item is
    commentary, not a 200-word button.

    require_context demands the "— <context>" suffix. Detection needs that precision,
    because a bare "### CTA" is part of the short-form angle format, not a microcopy
    item. Scoring stays permissive so a bare heading still gets checked.
    """
    if not kinds:
        return []
    names = sorted(kinds, key=len, reverse=True)
    suffix = r"\s*[\u2014\u2013:\-]\s*\S[^\n]*$" if require_context else r"\b[^\n]*$"
    pattern = re.compile(
        r"^#{1,6}\s*(%s)%s" % ("|".join(re.escape(n) for n in names), suffix),
        re.IGNORECASE | re.MULTILINE,
    )
    stop = re.compile(r"^#{1,6}\s", re.MULTILINE)
    items: List[Dict[str, object]] = []
    for match in pattern.finditer(raw):
        following = stop.search(raw, match.end())
        end = following.start() if following else len(raw)
        body = re.sub(r"\s+", " ", strip_markup(raw[match.end():end]).strip())
        if body:
            items.append({
                "kind": match.group(1).lower(),
                "text": body,
                "line": line_of(raw, match.end()) + 1,
                "start": match.end(),
                "end": end,
            })
    return items


TRIAGE_BLOCK = re.compile(r"^#{1,6}\s*triage\b[^\n]*$", re.IGNORECASE | re.MULTILINE)


def blank_triage(raw: str) -> Tuple[str, bool]:
    """Blank the triage block, preserving offsets, and report whether it was there.

    Triage is a routing declaration in a fixed vocabulary — "solution-aware" contains a
    banned word by construction. Scoring it for marketing slop is a category error.
    """
    match = TRIAGE_BLOCK.search(raw)
    if not match:
        return raw, False
    following = re.compile(r"^#{1,6}\s", re.MULTILINE).search(raw, match.end())
    end = following.start() if following else len(raw)
    blanked = re.sub(r"[^\n]", " ", raw[match.start():end])
    return raw[:match.start()] + blanked + raw[end:], True


def mask_to_spans(raw: str, spans: List[Tuple[int, int]]) -> str:
    """Blank everything outside the given spans, preserving offsets and line breaks.

    In the microcopy regime the labelled strings are the copy; the headings and any
    surrounding notes are annotation. Masking instead of slicing keeps every reported
    line number pointing at the real file.
    """
    keep = [False] * len(raw)
    for start, end in spans:
        for index in range(max(0, start), min(len(raw), end)):
            keep[index] = True
    return "".join(
        char if keep[index] or char == "\n" else " "
        for index, char in enumerate(raw)
    )


def detect_regime(raw: str, profiles: Dict[str, object]) -> str:
    text = strip_markup(blank_comments(raw))
    total = len(words_of(text))
    kinds = (
        profiles.get("profiles", {}).get("microcopy", {}).get("microcopy_kinds", {})
    )
    # Two or more distinct angle headings is a multi-variant marketing deliverable. One
    # alone is not: a sales letter has a "Proof" stage, which is a different animal.
    if len(parse_angles(raw)) >= 2:
        return "short-form"
    if microcopy_items(raw, kinds, require_context=True):
        return "microcopy"
    long_form = profiles["profiles"]["long-form"]["gates"]["required_sections"]
    headings = [h.group(2).lower() for h in HEADING_LINE.finditer(raw)]
    hits = sum(
        1 for section in long_form
        if any(any(s in h for s in section["synonyms"]) for h in headings)
    )
    if total >= 1200 and hits >= 4:
        return "long-form"
    if len(CLAUSE_NUMBER.findall(raw)) >= 2 or len(FUNCTIONAL_CUE.findall(text)) >= 3:
        return "functional"
    if total <= 40:
        return "microcopy"
    if total <= 300:
        return "short-form"
    return "editorial"


# --- measurement --------------------------------------------------------------------


def measure(text: str, prose: Optional[str] = None) -> Dict[str, float]:
    prose = text if prose is None else prose
    sentences = split_sentences(text)
    word_list = words_of(text)
    total = len(word_list)
    lengths = [len(words_of(s)) for s in sentences]
    lengths = [l for l in lengths if l > 0]
    if not lengths:
        return {}
    mean = statistics.mean(lengths)
    stdev = statistics.pstdev(lengths) if len(lengths) > 1 else 0.0
    return {
        "sentences": len(lengths),
        "words": total,
        "mean_sentence_words": round(mean, 2),
        "sentence_words_stdev": round(stdev, 2),
        "sentence_words_cv": round(stdev / mean, 3) if mean else 0.0,
        "short_sentence_ratio": round(sum(1 for l in lengths if l <= 6) / len(lengths), 3),
        "spec_tokens_per_100": per_hundred(len(SPEC_TOKEN.findall(text)), total),
        "hedges_per_100": per_hundred(len(HEDGES.findall(text)), total),
        "ly_adverbs_per_100": per_hundred(len(LY_ADVERB.findall(text)), total),
        "passive_hint_per_100": per_hundred(len(PASSIVE_HINT.findall(text)), total),
        "nominalizations_per_100": per_hundred(len(nominalizations(text)), total),
        "reading_grade": flesch_kincaid_grade(sentences, word_list),
        "em_dash_per_1000": per_thousand(
            prose.count("\u2014"), len(words_of(prose)) or total
        ),
    }


def parse_angles(raw: str) -> Dict[str, str]:
    matches = list(ANGLE_HEADING.finditer(raw))
    angles: Dict[str, str] = {}
    for index, match in enumerate(matches):
        label = re.sub(r"[\s\-]+", " ", match.group(2).strip().lower())
        if label == "proof":
            label = "social proof"
        end = matches[index + 1].start() if index + 1 < len(matches) else len(raw)
        body = raw[match.end():end].strip()
        angles[label] = angles.get(label, "") + ("\n\n" if label in angles else "") + body
    return angles


def jaccard(a: List[str], b: List[str]) -> float:
    set_a, set_b = set(a), set(b)
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / float(len(set_a | set_b))


def excerpt(raw: str, offset: int, width: int = 70) -> str:
    start = raw.rfind("\n", 0, offset) + 1
    end = raw.find("\n", offset)
    end = len(raw) if end == -1 else end
    line = raw[start:end].strip()
    if len(line) <= width:
        return line
    local = max(0, offset - start - width // 2)
    return "..." + line[local:local + width].strip() + "..."


# --- the linter ---------------------------------------------------------------------


class Linter:
    def __init__(self, profile: Dict[str, object], codex: Dict[str, object],
                 rules: Rules, variants: int) -> None:
        self.profile = profile
        self.codex = codex
        self.rules = rules
        self.variants = variants
        self.checks: Dict[str, str] = dict(profile.get("checks", {}))
        self.gates: Dict[str, object] = dict(profile.get("gates", {}))
        self.voice_source = "plain-language defaults"
        if codex.get("generated_from", {}).get("total_words"):
            if profile.get("voice_governs"):
                for key in VOICE_GATE_KEYS:
                    if key in codex.get("gates", {}):
                        self.gates[key] = codex["gates"][key]
                self.voice_source = "brand codex (governs style gates)"
            else:
                self.voice_source = "brand codex (terms only — discipline outranks voice here)"
        self.findings: List[Finding] = []

    def severity(self, check: str) -> Optional[str]:
        level = self.checks.get(check, "off")
        return None if level == "off" else level

    def add(self, check: str, message: str, fix: str,
            line: Optional[int] = None, evidence: str = "",
            severity: Optional[str] = None) -> None:
        level = severity or self.severity(check)
        if not level:
            return
        self.findings.append(Finding(check, level, message, line, evidence, fix))

    def gate(self, check: str, ok: bool, message: str, fix: str) -> None:
        if not ok:
            self.add(check, message, fix)

    def run(self, source_text: str) -> Dict[str, object]:
        source, self.has_triage = blank_triage(blank_comments(source_text))
        items = microcopy_items(source, self.profile.get("microcopy_kinds", {}))
        # In the microcopy regime the labelled strings are the copy. Notes around them
        # are annotation, and scoring them would judge the wrong text.
        raw = (
            mask_to_spans(source, [(i["start"], i["end"]) for i in items])
            if items and self.severity("microcopy-item")
            else source
        )
        text = strip_markup(raw)
        protected = [p.lower() for p in self.codex.get("protected_terms", [])]
        soft = {t.lower() for t in self.codex.get("soft_banned_phrases", [])}

        self.check_lexis(raw, protected, soft)
        measures = measure(text, prose=strip_markup(drop_headings(raw)))
        if not measures:
            raise SystemExit("error: no scoreable sentences found in input")
        self.check_measures(measures)
        self.check_habits(raw, text, measures)
        self.check_protected(raw, protected)
        angles = self.check_angles(source)
        self.check_structure(source)
        self.check_microcopy(items)

        by_category: Dict[str, int] = {}
        for finding in self.findings:
            by_category[finding.check] = by_category.get(finding.check, 0) + PENALTY.get(
                finding.check, 3
            )
        penalty = sum(min(value, CATEGORY_CAP) for value in by_category.values())
        score = max(0, 100 - penalty)
        blocking = [f for f in self.findings if f.severity == "BLOCK"]
        minimum = int(self.gates.get("min_score_to_pass", 80))

        return {
            "passed": not blocking and score >= minimum,
            "score": score,
            "min_score": minimum,
            "regime": self.profile.get("label"),
            "discipline": self.profile.get("discipline"),
            "voice_source": self.voice_source,
            "measures": measures,
            "gates": self.gates,
            "checks": self.checks,
            "angles": angles,
            "findings": [f.as_dict() for f in self.findings],
            "block_count": len(blocking),
            "warn_count": len(self.findings) - len(blocking),
        }

    # -- individual check groups ------------------------------------------------------

    def check_lexis(self, raw: str, protected: List[str], soft: set) -> None:
        for term, fix, offset, _matched in self.rules.word_hits(raw, allow=protected):
            is_soft = term.lower() in soft
            self.add(
                "banned-word-soft" if is_soft else "banned-word",
                'banned word "%s"%s'
                % (term, " (brand used it once, so justify it or swap it)" if is_soft else ""),
                fix,
                line=line_of(raw, offset),
                evidence=excerpt(raw, offset),
                severity="WARN" if is_soft else None,
            )
        for _pattern, why, fix, offset, matched in self.rules.construction_hits(raw):
            self.add(
                "banned-construction",
                'banned construction "%s" — %s' % (matched.strip()[:60], why),
                fix,
                line=line_of(raw, offset),
                evidence=excerpt(raw, offset),
            )

    def check_measures(self, m: Dict[str, float]) -> None:
        g = self.gates
        if "max_mean_sentence_words" in g:
            self.gate(
                "sentence-length",
                m["mean_sentence_words"] <= g["max_mean_sentence_words"],
                "mean sentence length %.1f words exceeds the %.1f allowed here"
                % (m["mean_sentence_words"], g["max_mean_sentence_words"]),
                "Cut the three longest sentences in half. Split at the first conjunction.",
            )
        if "min_sentence_words_cv" in g:
            self.gate(
                "flat-rhythm",
                m["sentence_words_cv"] >= g["min_sentence_words_cv"],
                "relative sentence-length variance %.2f is below the %.2f floor (stdev "
                "%.1f on mean %.1f) — every sentence is the same size, which is the "
                "single loudest AI tell"
                % (m["sentence_words_cv"], g["min_sentence_words_cv"],
                   m["sentence_words_stdev"], m["mean_sentence_words"]),
                "Break the rhythm on purpose: follow a 25-word sentence with a 3-word "
                "one. At least one sentence under 5 words per paragraph.",
            )
        if "min_short_sentence_ratio" in g:
            self.gate(
                "no-short-sentences",
                m["short_sentence_ratio"] >= g["min_short_sentence_ratio"],
                "only %.0f%% of sentences are 6 words or fewer (floor %.0f%%)"
                % (m["short_sentence_ratio"] * 100, g["min_short_sentence_ratio"] * 100),
                "Add short landings after long builds.",
            )
        if "min_spec_tokens_per_100" in g:
            self.gate(
                "low-specificity",
                m["spec_tokens_per_100"] >= g["min_spec_tokens_per_100"],
                "specificity %.2f concrete tokens per 100 words is below the %.2f floor "
                "— the copy describes a category, not a thing"
                % (m["spec_tokens_per_100"], g["min_spec_tokens_per_100"]),
                "Add real numbers, versions, counts, prices, dates, or named tools. "
                "Every claim needs one thing a photographer could photograph.",
            )
        if "max_hedges_per_100" in g:
            self.gate(
                "hedging",
                m["hedges_per_100"] <= g["max_hedges_per_100"],
                "hedging %.2f per 100 words exceeds max %.2f"
                % (m["hedges_per_100"], g["max_hedges_per_100"]),
                'Delete the hedge and assert: "designed to help you ship" becomes "you ship".',
            )
        if "max_ly_adverbs_per_100" in g:
            self.gate(
                "adverbs",
                m["ly_adverbs_per_100"] <= g["max_ly_adverbs_per_100"],
                "-ly adverbs %.2f per 100 words exceeds max %.2f"
                % (m["ly_adverbs_per_100"], g["max_ly_adverbs_per_100"]),
                "Delete the adverb, or replace the verb it is propping up.",
            )
        if "max_passive_hint_per_100" in g:
            self.gate(
                "passive",
                m["passive_hint_per_100"] <= g["max_passive_hint_per_100"],
                "passive constructions %.2f per 100 words exceeds max %.2f"
                % (m["passive_hint_per_100"], g["max_passive_hint_per_100"]),
                "Name the actor and put them in front of the verb.",
            )
        if "max_nominalizations_per_100" in g:
            self.gate(
                "nominalization",
                m["nominalizations_per_100"] <= g["max_nominalizations_per_100"],
                "buried verbs %.2f per 100 words exceeds max %.2f"
                % (m["nominalizations_per_100"], g["max_nominalizations_per_100"]),
                'Turn the noun back into a verb: "make a determination" becomes "decide".',
            )
        if "max_reading_grade" in g:
            self.gate(
                "reading-grade",
                m["reading_grade"] <= g["max_reading_grade"],
                "reading grade %.1f exceeds the %.1f ceiling"
                % (m["reading_grade"], g["max_reading_grade"]),
                "Shorten sentences and swap long words for short ones. A document "
                "nobody can read is a document nobody consented to.",
            )
        if "max_em_dash_per_1000" in g:
            self.gate(
                "em-dash",
                m["em_dash_per_1000"] <= g["max_em_dash_per_1000"],
                "em dashes %.2f per 1000 words exceeds max %.2f"
                % (m["em_dash_per_1000"], g["max_em_dash_per_1000"]),
                "Convert half the asides into their own sentences, or into commas.",
            )

    def check_habits(self, raw: str, text: str, m: Dict[str, float]) -> None:
        metrics = self.codex.get("metrics", {})
        if metrics.get("exclamation_per_1000", 0) <= 0.5 and "!" in text:
            self.add("exclamation",
                     "exclamation mark used, but the reference register contains none",
                     "Remove it. Force comes from specificity, not punctuation.")
        if str(self.codex.get("capitalization", "")).startswith("sentence"):
            headlines = [s for s in split_sentences(text) if len(words_of(s)) <= 12]
            title_cased = [
                s for s in headlines
                if len([w for w in words_of(s)[1:]
                        if w[:1].isupper() and w.lower() not in STOPWORDS])
                >= max(2, len(words_of(s)) // 2)
            ]
            if headlines and len(title_cased) / len(headlines) > 0.5:
                self.add("capitalization",
                         "%d of %d headlines are Title Case; the register uses sentence case"
                         % (len(title_cased), len(headlines)),
                         "Lowercase everything after the first word except proper nouns.")

        sentences = split_sentences(text)
        openers = [words_of(s)[0].lower() for s in sentences if words_of(s)]
        for i in range(len(openers) - 2):
            if openers[i] == openers[i + 1] == openers[i + 2]:
                self.add("repeated-opener",
                         'three consecutive sentences open with "%s"' % openers[i],
                         "Vary the opening word. Anaphora works once, never three times "
                         "in a row by accident.")
                break
        if not any(w.lower() in BASE_VERB_OPENERS
                   for s in sentences for w in words_of(s)[:1]):
            self.add("no-imperative-cta",
                     "no sentence opens with an imperative verb, so there is no clear ask",
                     'End with a verb-first CTA: "Claim the founding rate", not '
                     '"Ready to get started?"')

        seen: Dict[str, int] = {}
        for number, line in enumerate(raw.splitlines(), start=1):
            key = re.sub(r"[^a-z0-9 ]", "", line.strip().lower())
            if len(key.split()) < 5:
                continue
            if key in seen:
                self.add("duplicate-line",
                         "line repeats line %d verbatim" % seen[key],
                         "Say it once, or say something different. Rewrite or delete.",
                         line=number, evidence=line.strip()[:90])
            else:
                seen[key] = number

        if self.severity("missing-triage"):
            if not self.has_triage:
                self.add("missing-triage",
                         "no Triage block: the draft does not declare its regime, the "
                         "reader's awareness level, or the framework it used",
                         "Add the Triage block from SKILL.md before the copy. Routing "
                         "decided in the open can be checked; routing done by habit "
                         "cannot.")

    def check_protected(self, raw: str, protected: List[str]) -> None:
        if not self.severity("protected-overuse") or not protected:
            return
        base = int(self.gates.get("max_protected_term_repeats", 2))
        angle_count = max(1, len(parse_angles(raw))) if self.variants > 1 else 1
        cap = base * angle_count
        for term in protected:
            count = len(re.findall(r"\b%s\b" % re.escape(term), raw, re.IGNORECASE))
            if count > cap:
                self.add("protected-overuse",
                         'brand term "%s" used %d times (max %d across %d variant(s))'
                         % (term, count, cap, angle_count),
                         "Keep the first use. Replace the rest with the specific noun it "
                         "refers to. Signature used once is identity; used five times it "
                         "is wallpaper.")

    def check_angles(self, raw: str) -> Dict[str, object]:
        report: Dict[str, object] = {"found": [], "overlaps": []}
        if not self.severity("missing-angle"):
            return report
        angles = parse_angles(raw)
        report["found"] = sorted(angles)
        if self.variants <= 1:
            return report
        for required in self.gates.get("required_angles", []):
            if required not in angles:
                self.add("missing-angle",
                         'required angle "%s" is missing' % required,
                         'Add a "## Angle N — %s" section. Three angles is a structural '
                         "requirement, not a variety bonus: one draft gives the reader "
                         "nothing to choose between and you nothing to test."
                         % required.title())
        limit = float(self.gates.get("max_angle_overlap", 0.5))
        names = sorted(angles)
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                score = jaccard(content_words(angles[names[i]]),
                                content_words(angles[names[j]]))
                report["overlaps"].append(
                    {"a": names[i], "b": names[j], "overlap": round(score, 3)}
                )
                if score > limit:
                    self.add("angle-overlap",
                             "%s and %s share %.0f%% of their content words (max %.0f%%)"
                             % (names[i], names[j], score * 100, limit * 100),
                             "These are the same angle in two outfits. Each angle must "
                             "lead with a different noun and cite different proof. "
                             "Rewrite one from scratch.")
        return report

    def check_structure(self, raw: str) -> None:
        required = self.gates.get("required_sections")
        if not self.severity("missing-section") or not required:
            return
        headings = [h.group(2).lower() for h in HEADING_LINE.finditer(raw)]
        order: List[str] = []
        for name in headings:
            for section in required:
                if any(s in name for s in section["synonyms"]):
                    if section["name"] not in order:
                        order.append(section["name"])
                    break
        missing = [s["name"] for s in required if s["name"] not in order]
        if missing:
            self.add("missing-section",
                     "missing required stage(s): %s" % ", ".join(missing),
                     "Long-form copy that skips a stage loses the reader at exactly that "
                     "stage. See references/long-form-architecture.md for what each one "
                     "must contain.")
        expected = [s["name"] for s in required if s["name"] in order]
        if order != expected:
            self.add("missing-section",
                     "stages appear as %s, the architecture requires %s"
                     % (" > ".join(order), " > ".join(expected)),
                     "Reorder. Proof before the mechanism has nothing to prove; the "
                     "offer before proof is a price with no reason.")

    def check_microcopy(self, items: List[Dict[str, object]]) -> None:
        if not self.severity("microcopy-item"):
            return
        kinds: Dict[str, object] = self.profile.get("microcopy_kinds", {})
        if not items:
            self.add("microcopy-item",
                     "no labelled microcopy items found",
                     'Label each string: "### Button — save draft", then the string on '
                     "the next line. Unlabelled microcopy cannot be checked against its "
                     "own kind's rules.")
            return
        for item in items:
            kind, body, line = item["kind"], item["text"], item["line"]
            spec: Dict[str, object] = kinds.get(kind, {})
            words = words_of(body)
            limit = int(spec.get("max_words", 15))
            if len(words) > limit:
                self.add("microcopy-item",
                         '%s is %d words (max %d): "%s"' % (kind, len(words), limit, body),
                         "Cut to the outcome. Every extra word in microcopy is read by "
                         "everyone and helps no one.",
                         line=line)
            for banned in spec.get("banned", []):
                if re.search(r"\b%s\b" % re.escape(banned), body, re.IGNORECASE):
                    note = spec.get("note", "")
                    self.add("microcopy-item",
                             '%s contains "%s": "%s"' % (kind, banned, body),
                             note or "Name the outcome instead.",
                             line=line)
            if spec.get("verb_first") and words:
                if words[0].lower() not in BASE_VERB_OPENERS:
                    self.add("microcopy-item",
                             '%s does not start with a verb: "%s"' % (kind, body),
                             'Verb first, outcome second: "Create account", not '
                             '"Account creation".',
                             line=line)
            if spec.get("require_fix"):
                if not any(w.lower() in BASE_VERB_OPENERS for w in words):
                    self.add("microcopy-item",
                             '%s tells the reader what happened but not what to do: "%s"'
                             % (kind, body),
                             "Add the recovery step. [what went wrong] + [why, if known] "
                             "+ [how to fix it].",
                             line=line)
            if body.endswith("?") and kind in ("button", "cta"):
                self.add("microcopy-item",
                         '%s is a question: "%s"' % (kind, body),
                         "A question asks permission. Use verb + object.",
                         line=line)


# --- reporting ----------------------------------------------------------------------


def report(result: Dict[str, object], source: str, regime: str, detected: bool) -> None:
    print("COPY LINT — %s" % source)
    print("regime: %s%s" % (regime, " (auto-detected)" if detected else ""))
    print("discipline: %s" % result["discipline"])
    print("voice: %s" % result["voice_source"])
    print("")

    for severity in ("BLOCK", "WARN"):
        group = [f for f in result["findings"] if f["severity"] == severity]
        if not group:
            continue
        label = ("BLOCK — must fix before this copy leaves the room" if severity == "BLOCK"
                 else "WARN — fix unless you can justify it")
        print("%s (%d)" % (label, len(group)))
        group.sort(key=lambda f: (f["line"] is None, f["line"] or 0, f["check"]))
        for finding in group:
            location = "%-6s" % ("L%d" % finding["line"] if finding["line"] else "--")
            print("  %s %s" % (location, finding["message"]))
            if finding["evidence"]:
                print("        > %s" % finding["evidence"])
            if finding["fix"]:
                print("        fix: %s" % finding["fix"])
        print("")

    m, g = result["measures"], result["gates"]
    rows: List[Tuple[str, object, str, bool]] = []

    def row(label: str, key: str, gate_key: str, direction: str) -> None:
        if gate_key not in g or key not in m:
            return
        limit = g[gate_key]
        ok = m[key] <= limit if direction == "max" else m[key] >= limit
        rows.append((label, m[key], "%s %s" % (direction, limit), ok))

    row("mean sentence words", "mean_sentence_words", "max_mean_sentence_words", "max")
    row("rhythm variance (cv)", "sentence_words_cv", "min_sentence_words_cv", "min")
    row("short-sentence ratio", "short_sentence_ratio", "min_short_sentence_ratio", "min")
    row("concrete tokens /100w", "spec_tokens_per_100", "min_spec_tokens_per_100", "min")
    row("hedges /100w", "hedges_per_100", "max_hedges_per_100", "max")
    row("-ly adverbs /100w", "ly_adverbs_per_100", "max_ly_adverbs_per_100", "max")
    row("passive /100w", "passive_hint_per_100", "max_passive_hint_per_100", "max")
    row("buried verbs /100w", "nominalizations_per_100", "max_nominalizations_per_100", "max")
    row("reading grade", "reading_grade", "max_reading_grade", "max")

    if rows:
        print("MEASURES  (%d words, %d sentences)" % (m["words"], m["sentences"]))
        for label, value, limit, ok in rows:
            print("  %-24s %8s   %-10s %s" % (label, value, limit, "ok" if ok else "FAIL"))
        print("")

    if result["angles"]["found"] or result["angles"]["overlaps"]:
        print("ANGLES")
        print("  found: %s" % (", ".join(result["angles"]["found"]) or "none"))
        for pair in result["angles"]["overlaps"]:
            print("  overlap %s / %s: %.2f (max %.2f)"
                  % (pair["a"], pair["b"], pair["overlap"],
                     result["gates"].get("max_angle_overlap", 0.5)))
        print("")

    verdict = "PASS" if result["passed"] else "FAIL"
    print("SCORE %d/100 — %s (needs >= %d and zero BLOCK findings)"
          % (result["score"], verdict, result["min_score"]))
    if not result["passed"]:
        print("NEXT: fix every BLOCK finding, then re-run this script. Do not show the "
              "draft to the user until it exits 0.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("draft", help="path to the draft, or - for stdin")
    parser.add_argument("--regime", default="auto",
                        help="microcopy, short-form, long-form, editorial, functional, "
                             "or auto")
    parser.add_argument("--codex", default=None,
                        help="brand voice codex JSON. Omit for plain-language defaults")
    parser.add_argument("--profiles", default=DEFAULT_PROFILES)
    parser.add_argument("--table", default=None, help="override the main rule table")
    parser.add_argument("--variants", type=int, default=3,
                        help="how many angles this deliverable must carry (1 disables "
                             "the angle requirement)")
    parser.add_argument("--json", dest="as_json", action="store_true")
    args = parser.parse_args()

    if args.draft == "-":
        raw = sys.stdin.read()
        source = "<stdin>"
    else:
        if not os.path.isfile(args.draft):
            print("error: no such file: %s" % args.draft, file=sys.stderr)
            return 2
        with open(args.draft, "r", encoding="utf-8") as handle:
            raw = handle.read()
        source = args.draft

    profiles = load_json(args.profiles, "profiles file")
    detected = args.regime == "auto"
    regime = detect_regime(raw, profiles) if detected else args.regime
    profile = resolve_profile(profiles, regime)
    codex = load_json(args.codex or DEFAULT_CODEX, "voice codex")

    tables: List[Optional[str]] = [args.table or DEFAULT_TABLE]
    for extra in profile.get("extra_rule_tables", []):
        tables.append(os.path.join(REFERENCES, extra))
    rules = load_many(tables)

    result = Linter(profile, codex, rules, args.variants).run(raw)
    if args.as_json:
        result["regime_key"] = regime
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        report(result, source, regime, detected)
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
