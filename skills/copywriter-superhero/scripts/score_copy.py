#!/usr/bin/env python3
"""Score a copy draft against the voice codex and the replacement table.

This is a deterministic critic. It replaces "try to write well" with a gate that
either passes or names the exact line to fix, so the agent can iterate without a
human in the loop.

Usage:
    python3 score_copy.py draft.md
    python3 score_copy.py draft.md --mode single      # one block, skip angle checks
    python3 score_copy.py - < draft.md --json
    python3 score_copy.py draft.md --codex path/to/voice-codex.json

Exit codes:
    0  PASS — zero BLOCK findings and score >= codex gate
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
from typing import Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rules import load_rules  # noqa: E402
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
    line_of,
    per_hundred,
    per_thousand,
    split_sentences,
    strip_markup,
    words_of,
)

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CODEX = os.path.join(SKILL_DIR, "references", "voice-codex.json")

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
    "passive": 3,
    "missing-angle": 12,
    "angle-overlap": 10,
    "duplicate-line": 8,
    "repeated-opener": 4,
    "no-imperative-cta": 5,
    "capitalization": 2,
    "exclamation": 3,
}
CATEGORY_CAP = 24


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


ANGLE_HEADING = re.compile(
    r"^#{1,6}\s*(?:angle\s*)?(\d+)?\s*[\u2014\u2013:\-]?\s*"
    r"(logic|pain|social[\s\-]?proof|proof|status|curiosity|contrarian)\b.*$",
    re.IGNORECASE | re.MULTILINE,
)


def parse_angles(raw: str) -> Dict[str, str]:
    """Split a draft into {angle_type: body} using its Angle headings."""
    matches = list(ANGLE_HEADING.finditer(raw))
    angles: Dict[str, str] = {}
    for index, match in enumerate(matches):
        label = re.sub(r"[\s\-]+", " ", match.group(2).strip().lower())
        if label == "proof":
            label = "social proof"
        end = matches[index + 1].start() if index + 1 < len(matches) else len(raw)
        body = raw[match.end():end].strip()
        if label in angles:
            angles[label] += "\n\n" + body
        else:
            angles[label] = body
    return angles


def jaccard(a: List[str], b: List[str]) -> float:
    set_a, set_b = set(a), set(b)
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / float(len(set_a | set_b))


def load_codex(path: str) -> Dict[str, object]:
    if not os.path.isfile(path):
        raise SystemExit(
            "error: no voice codex at %s\n"
            "run: python3 scripts/extract_voice_codex.py "
            "--samples references/voice-samples --out references/voice-codex.json" % path
        )
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def measure(text: str, prose: Optional[str] = None) -> Dict[str, float]:
    prose = text if prose is None else prose
    sentences = split_sentences(text)
    word_list = words_of(text)
    total = len(word_list)
    lengths = [len(words_of(s)) for s in sentences]
    lengths = [l for l in lengths if l > 0]
    if not lengths:
        return {}
    return {
        "sentences": len(lengths),
        "words": total,
        "mean_sentence_words": round(statistics.mean(lengths), 2),
        "sentence_words_stdev": round(
            statistics.pstdev(lengths) if len(lengths) > 1 else 0.0, 2
        ),
        "sentence_words_cv": round(
            (statistics.pstdev(lengths) / statistics.mean(lengths))
            if len(lengths) > 1 and statistics.mean(lengths) else 0.0,
            3,
        ),
        "short_sentence_ratio": round(sum(1 for l in lengths if l <= 6) / len(lengths), 3),
        "spec_tokens_per_100": per_hundred(len(SPEC_TOKEN.findall(text)), total),
        "hedges_per_100": per_hundred(len(HEDGES.findall(text)), total),
        "ly_adverbs_per_100": per_hundred(len(LY_ADVERB.findall(text)), total),
        "passive_hint_per_100": per_hundred(len(PASSIVE_HINT.findall(text)), total),
        "em_dash_per_1000": per_thousand(
            prose.count("\u2014"), len(words_of(prose)) or total
        ),
    }


def check_gate(findings: List[Finding], check: str, ok: bool, message: str,
               fix: str, severity: str = "BLOCK") -> None:
    if not ok:
        findings.append(Finding(check, severity, message, fix=fix))


def lint(source_text: str, codex: Dict[str, object], mode: str,
         table_path: Optional[str]) -> Dict[str, object]:
    rules = load_rules(table_path)
    gates = codex["gates"]
    protected = [p.lower() for p in codex.get("protected_terms", [])]
    # Author notes are not copy. Blanking keeps offsets, so line numbers stay true.
    raw = blank_comments(source_text)
    text = strip_markup(raw)
    findings: List[Finding] = []

    # --- lexical and syntactic tells -------------------------------------------------
    soft_banned = {t.lower() for t in codex.get("soft_banned_phrases", [])}
    for term, fix, offset, matched in rules.word_hits(raw, allow=protected):
        soft = term.lower() in soft_banned
        findings.append(
            Finding(
                "banned-word-soft" if soft else "banned-word",
                "WARN" if soft else "BLOCK",
                'banned word "%s"%s'
                % (term, " (brand used it once, so justify it or swap it)" if soft else ""),
                line=line_of(raw, offset),
                evidence=excerpt(raw, offset),
                fix=fix,
            )
        )
    for _pattern, why, fix, offset, matched in rules.construction_hits(raw):
        findings.append(
            Finding(
                "banned-construction", "BLOCK",
                'banned construction "%s" — %s' % (matched.strip()[:60], why),
                line=line_of(raw, offset),
                evidence=excerpt(raw, offset),
                fix=fix,
            )
        )

    angles = parse_angles(raw)
    # Each angle is read on its own, so the per-piece cap scales with the angle count.
    # Otherwise naming the offer once per angle reads as overuse.
    angle_count = max(1, len(angles)) if mode == "angles" else 1
    max_repeats = int(gates.get("max_protected_term_repeats", 2)) * angle_count
    for term in protected:
        count = len(re.findall(r"\b%s\b" % re.escape(term), raw, re.IGNORECASE))
        if count > max_repeats:
            findings.append(
                Finding(
                    "protected-overuse", "WARN",
                    'brand term "%s" used %d times (max %d across %d angle(s))'
                    % (term, count, max_repeats, angle_count),
                    fix="Keep the first use. Replace the rest with the specific noun "
                        "it refers to. Signature used once is identity; used five "
                        "times it is wallpaper.",
                )
            )

    # --- measured rhythm and specificity --------------------------------------------
    m = measure(text, prose=strip_markup(drop_headings(raw)))
    if not m:
        raise SystemExit("error: no scoreable sentences found in input")

    check_gate(
        findings, "sentence-length",
        m["mean_sentence_words"] <= gates["max_mean_sentence_words"],
        "mean sentence length %.1f words exceeds brand max %.1f"
        % (m["mean_sentence_words"], gates["max_mean_sentence_words"]),
        "Cut the three longest sentences in half. Split at the first conjunction.",
    )
    check_gate(
        findings, "flat-rhythm",
        m["sentence_words_cv"] >= gates["min_sentence_words_cv"],
        "relative sentence-length variance %.2f is below brand floor %.2f (stdev %.1f "
        "on mean %.1f) — every sentence is the same size, which is the single loudest "
        "AI tell"
        % (m["sentence_words_cv"], gates["min_sentence_words_cv"],
           m["sentence_words_stdev"], m["mean_sentence_words"]),
        "Break the rhythm on purpose: follow a 25-word sentence with a 3-word one. "
        "Aim for at least one sentence under 5 words per paragraph.",
    )
    check_gate(
        findings, "no-short-sentences",
        m["short_sentence_ratio"] >= gates["min_short_sentence_ratio"],
        "only %.0f%% of sentences are 6 words or fewer (brand floor %.0f%%)"
        % (m["short_sentence_ratio"] * 100, gates["min_short_sentence_ratio"] * 100),
        "Add short landings after long builds.",
        severity="WARN",
    )
    check_gate(
        findings, "low-specificity",
        m["spec_tokens_per_100"] >= gates["min_spec_tokens_per_100"],
        "specificity %.2f concrete tokens per 100 words is below brand floor %.2f — "
        "the copy describes a category, not a product"
        % (m["spec_tokens_per_100"], gates["min_spec_tokens_per_100"]),
        "Add real numbers, versions, counts, prices, dates, or named tools. "
        "Every claim needs one thing a photographer could photograph.",
    )
    check_gate(
        findings, "hedging",
        m["hedges_per_100"] <= gates["max_hedges_per_100"],
        "hedging %.2f per 100 words exceeds max %.2f"
        % (m["hedges_per_100"], gates["max_hedges_per_100"]),
        'Delete the hedge and assert: "designed to help you ship" becomes "you ship".',
        severity="WARN",
    )
    check_gate(
        findings, "adverbs",
        m["ly_adverbs_per_100"] <= gates["max_ly_adverbs_per_100"],
        "-ly adverbs %.2f per 100 words exceeds max %.2f"
        % (m["ly_adverbs_per_100"], gates["max_ly_adverbs_per_100"]),
        "Delete the adverb or replace the verb it is propping up.",
        severity="WARN",
    )
    check_gate(
        findings, "passive",
        m["passive_hint_per_100"] <= gates["max_passive_hint_per_100"],
        "passive constructions %.2f per 100 words exceeds max %.2f"
        % (m["passive_hint_per_100"], gates["max_passive_hint_per_100"]),
        "Name the actor and put them in front of the verb.",
        severity="WARN",
    )
    check_gate(
        findings, "em-dash",
        m["em_dash_per_1000"] <= gates["max_em_dash_per_1000"],
        "em dashes %.2f per 1000 words exceeds max %.2f"
        % (m["em_dash_per_1000"], gates["max_em_dash_per_1000"]),
        "Convert half the asides into their own sentences or into commas.",
        severity="WARN",
    )

    codex_metrics = codex.get("metrics", {})
    if codex_metrics.get("exclamation_per_1000", 0) <= 0.5 and "!" in text:
        findings.append(
            Finding("exclamation", "WARN",
                    "exclamation mark used, but the brand corpus contains none",
                    fix="Remove it. The register carries force through specificity, "
                        "not punctuation."))
    if codex.get("capitalization", "").startswith("sentence"):
        headlines = [s for s in split_sentences(text) if len(words_of(s)) <= 12]
        title_cased = [
            s for s in headlines
            if len([w for w in words_of(s)[1:]
                    if w[:1].isupper() and w.lower() not in STOPWORDS])
            >= max(2, len(words_of(s)) // 2)
        ]
        if headlines and len(title_cased) / len(headlines) > 0.5:
            findings.append(
                Finding("capitalization", "WARN",
                        "%d of %d headlines are Title Case; the brand uses sentence case"
                        % (len(title_cased), len(headlines)),
                        fix="Lowercase everything after the first word except proper nouns."))

    sentences = split_sentences(text)
    openers: List[str] = [words_of(s)[0].lower() for s in sentences if words_of(s)]
    for i in range(len(openers) - 2):
        if openers[i] == openers[i + 1] == openers[i + 2]:
            findings.append(
                Finding("repeated-opener", "WARN",
                        'three consecutive sentences open with "%s"' % openers[i],
                        fix="Vary the opening word. Anaphora works once, never three "
                            "times in a row by accident."))
            break
    if not any(w.lower() in BASE_VERB_OPENERS for s in sentences for w in words_of(s)[:1]):
        findings.append(
            Finding("no-imperative-cta", "WARN",
                    "no sentence opens with an imperative verb, so there is no clear ask",
                    fix="End each angle with a verb-first CTA: "
                        '"Claim the founding rate", not "Ready to get started?"'))

    normalized_lines = {}
    for number, line in enumerate(raw.splitlines(), start=1):
        key = re.sub(r"[^a-z0-9 ]", "", line.strip().lower())
        if len(key.split()) < 5:
            continue
        if key in normalized_lines:
            findings.append(
                Finding("duplicate-line", "BLOCK",
                        "line repeats line %d verbatim" % normalized_lines[key],
                        line=number, evidence=line.strip()[:90],
                        fix="Each angle must make a different claim, not the same claim "
                            "reworded. Rewrite or delete."))
        else:
            normalized_lines[key] = number

    # --- angle structure -------------------------------------------------------------
    angle_report: Dict[str, object] = {"found": sorted(angles.keys()), "overlaps": []}
    if mode == "angles":
        for required in gates.get("required_angles", []):
            if required not in angles:
                findings.append(
                    Finding("missing-angle", "BLOCK",
                            'required angle "%s" is missing' % required,
                            fix='Add a "## Angle N — %s" section. Three angles is a '
                                "structural requirement, not a variety bonus: one draft "
                                "gives the reader nothing to choose between."
                                % required.title()))
        max_overlap = float(gates.get("max_angle_overlap", 0.5))
        names = sorted(angles.keys())
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                score = jaccard(content_words(angles[names[i]]),
                                content_words(angles[names[j]]))
                angle_report["overlaps"].append(
                    {"a": names[i], "b": names[j], "overlap": round(score, 3)}
                )
                if score > max_overlap:
                    findings.append(
                        Finding("angle-overlap", "BLOCK",
                                "%s and %s share %.0f%% of their content words (max %.0f%%)"
                                % (names[i], names[j], score * 100, max_overlap * 100),
                                fix="These are the same angle in two outfits. Each angle "
                                    "must lead with a different noun and cite different "
                                    "proof. Rewrite one from scratch."))

    # --- scoring ---------------------------------------------------------------------
    by_category: Dict[str, int] = {}
    for finding in findings:
        by_category[finding.check] = by_category.get(finding.check, 0) + PENALTY.get(
            finding.check, 3
        )
    total_penalty = sum(min(value, CATEGORY_CAP) for value in by_category.values())
    score = max(0, 100 - total_penalty)
    blocking = [f for f in findings if f.severity == "BLOCK"]
    min_score = int(gates.get("min_score_to_pass", 80))
    passed = not blocking and score >= min_score

    return {
        "passed": passed,
        "score": score,
        "min_score": min_score,
        "measures": m,
        "gates": gates,
        "angles": angle_report,
        "findings": [f.as_dict() for f in findings],
        "block_count": len(blocking),
        "warn_count": len(findings) - len(blocking),
    }


def excerpt(raw: str, offset: int, width: int = 70) -> str:
    start = raw.rfind("\n", 0, offset) + 1
    end = raw.find("\n", offset)
    end = len(raw) if end == -1 else end
    line = raw[start:end].strip()
    if len(line) <= width:
        return line
    local = max(0, offset - start - width // 2)
    return "..." + line[local:local + width].strip() + "..."


def report(result: Dict[str, object], source: str, codex: Dict[str, object]) -> None:
    meta = codex.get("generated_from", {})
    print("COPY LINT — %s" % source)
    print("codex: %d-word corpus, %d files, %s"
          % (meta.get("total_words", 0), len(meta.get("files", [])),
             "; ".join(codex.get("tone_descriptors", [])[:3])))
    print("")

    for severity in ("BLOCK", "WARN"):
        group = [f for f in result["findings"] if f["severity"] == severity]
        if not group:
            continue
        label = "BLOCK — must fix before this copy leaves the room" if severity == "BLOCK" \
            else "WARN — fix unless you can justify it"
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

    m, gates = result["measures"], result["gates"]
    rows = [
        ("mean sentence words", m["mean_sentence_words"],
         "max %.1f" % gates["max_mean_sentence_words"],
         m["mean_sentence_words"] <= gates["max_mean_sentence_words"]),
        ("rhythm variance (cv)", m["sentence_words_cv"],
         "min %.2f" % gates["min_sentence_words_cv"],
         m["sentence_words_cv"] >= gates["min_sentence_words_cv"]),
        ("short-sentence ratio", m["short_sentence_ratio"],
         "min %.2f" % gates["min_short_sentence_ratio"],
         m["short_sentence_ratio"] >= gates["min_short_sentence_ratio"]),
        ("concrete tokens /100w", m["spec_tokens_per_100"],
         "min %.2f" % gates["min_spec_tokens_per_100"],
         m["spec_tokens_per_100"] >= gates["min_spec_tokens_per_100"]),
        ("hedges /100w", m["hedges_per_100"],
         "max %.2f" % gates["max_hedges_per_100"],
         m["hedges_per_100"] <= gates["max_hedges_per_100"]),
        ("-ly adverbs /100w", m["ly_adverbs_per_100"],
         "max %.2f" % gates["max_ly_adverbs_per_100"],
         m["ly_adverbs_per_100"] <= gates["max_ly_adverbs_per_100"]),
    ]
    print("MEASURES")
    for name, value, limit, ok in rows:
        print("  %-24s %8s   %-10s %s" % (name, value, limit, "ok" if ok else "FAIL"))
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
    parser.add_argument("--codex", default=DEFAULT_CODEX)
    parser.add_argument("--table", default=None)
    parser.add_argument("--mode", choices=("angles", "single"), default="angles")
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

    codex = load_codex(args.codex)
    result = lint(raw, codex, args.mode, args.table)

    if args.as_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        report(result, source, codex)
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
