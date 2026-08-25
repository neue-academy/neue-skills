#!/usr/bin/env python3
"""Measure a brand's real published copy and emit a voice codex.

Every number the linter enforces is calibrated from this corpus, so the quality
bar is "sounds like this brand" rather than "sounds like generic good copy".

Usage:
    python3 extract_voice_codex.py --samples <dir> --out voice-codex-<brand>.json
    python3 extract_voice_codex.py --samples <dir> --print   # human summary only

Standard library only. No install step.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import sys
from collections import Counter
from typing import Dict, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rules import load_rules  # noqa: E402
from textstats import (  # noqa: E402
    BASE_VERB_OPENERS,
    CONTRACTIONS,
    FIRST_PLURAL,
    HEDGES,
    LY_ADVERB,
    PASSIVE_HINT,
    SECOND_PERSON,
    SIMILE,
    SPEC_TOKEN,
    STOPWORDS,
    TECH_TERM,
    figurative_hits,
    per_hundred,
    per_thousand,
    split_sentences,
    strip_markup,
    words_of,
)

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_corpus(sample_dir: str) -> List[Dict[str, str]]:
    if not os.path.isdir(sample_dir):
        raise SystemExit("error: samples directory not found: %s" % sample_dir)
    docs: List[Dict[str, str]] = []
    for name in sorted(os.listdir(sample_dir)):
        if not name.lower().endswith((".md", ".txt", ".markdown")):
            continue
        if name.lower() == "readme.md":
            continue
        path = os.path.join(sample_dir, name)
        with open(path, "r", encoding="utf-8") as handle:
            raw = handle.read()
        source_match = re.search(r"<!--\s*source:\s*(.*?)\s*-->", raw, re.DOTALL)
        docs.append(
            {
                "file": name,
                "source": source_match.group(1).strip() if source_match else "unlabelled",
                "text": strip_markup(raw),
            }
        )
    if not docs:
        raise SystemExit("error: no .md/.txt samples found in %s" % sample_dir)
    return docs


def ngrams(word_list: List[str], size: int) -> List[str]:
    lowered = [w.lower() for w in word_list]
    return [
        " ".join(lowered[i : i + size]) for i in range(len(lowered) - size + 1)
    ]


def signature_phrases(word_list: List[str], limit: int = 12) -> List[Dict[str, object]]:
    found: List[Dict[str, object]] = []
    for size in (3, 2):
        counts = Counter(ngrams(word_list, size))
        for phrase, count in counts.most_common(80):
            if count < 2:
                continue
            tokens = phrase.split()
            if all(t in STOPWORDS for t in tokens):
                continue
            if tokens[0] in STOPWORDS and tokens[-1] in STOPWORDS:
                continue
            found.append({"phrase": phrase, "count": count, "n": size})
    found.sort(key=lambda item: (-int(item["count"]), -int(item["n"])))
    return found[:limit]


def tone_descriptors(m: Dict[str, float]) -> List[str]:
    out: List[str] = []
    mean = m["mean_sentence_words"]
    if mean <= 11:
        out.append("clipped")
    elif mean <= 17:
        out.append("brisk")
    elif mean <= 24:
        out.append("measured")
    else:
        out.append("dense, compound-heavy")

    if m["sentence_words_stdev"] >= 9:
        out.append("high rhythm variance (long build, short landing)")
    elif m["sentence_words_stdev"] >= 5:
        out.append("moderate rhythm variance")
    else:
        out.append("flat rhythm")

    if m["second_person_per_100"] >= 3.5:
        out.append("reader-facing (heavy second person)")
    elif m["second_person_per_100"] >= 1.5:
        out.append("reader-aware")
    else:
        out.append("declarative, product-facing")

    if m["contractions_per_100"] >= 2.5:
        out.append("informal contractions")
    elif m["contractions_per_100"] >= 0.8:
        out.append("selectively informal")
    else:
        out.append("formal, uncontracted")

    if m["spec_tokens_per_100"] >= 3:
        out.append("specification-led (numbers carry the claim)")
    elif m["spec_tokens_per_100"] >= 1:
        out.append("occasionally quantified")
    else:
        out.append("qualitative")

    if m["imperative_opening_ratio"] >= 0.25:
        out.append("imperative, instruction-shaped")
    if m["exclamation_per_1000"] <= 0.5:
        out.append("no exclamation")
    if m["em_dash_per_1000"] >= 5:
        out.append("em-dash aside as a habit")
    return out


def jargon_label(rate: float) -> str:
    if rate >= 4:
        return "high — technical nouns are the default register; do not simplify them away"
    if rate >= 1.5:
        return "medium — technical nouns allowed when they name a real artefact"
    return "low — plain nouns only"


def metaphor_label(rate: float) -> str:
    if rate >= 8:
        return "frequent — metaphor is a load-bearing device"
    if rate >= 3:
        return "occasional — roughly one metaphor per section, never stacked"
    return "rare — prefer literal description"


def build_codex(sample_dir: str, table_path: str) -> Dict[str, object]:
    docs = read_corpus(sample_dir)
    text = "\n\n".join(d["text"] for d in docs)
    sentences = split_sentences(text)
    word_list = words_of(text)
    total_words = len(word_list)
    lengths = [len(words_of(s)) for s in sentences]
    lengths = [l for l in lengths if l > 0]
    if len(lengths) < 5:
        raise SystemExit(
            "error: only %d usable sentences — add more samples before trusting a codex"
            % len(lengths)
        )

    stdev = statistics.pstdev(lengths) if len(lengths) > 1 else 0.0
    ordered = sorted(lengths)

    def pct(p: float) -> int:
        idx = min(len(ordered) - 1, max(0, int(round((len(ordered) - 1) * p))))
        return ordered[idx]

    tech_terms = TECH_TERM.findall(text)
    metaphor_hits = len(SIMILE.findall(text)) + len(figurative_hits(text))
    imperative_openers = sum(
        1 for s in sentences if words_of(s) and words_of(s)[0].lower() in BASE_VERB_OPENERS
    )
    headline_like = [s for s in sentences if len(words_of(s)) <= 12]
    title_case = sum(
        1
        for s in headline_like
        if len(
            [w for w in words_of(s)[1:] if w[:1].isupper() and w.lower() not in STOPWORDS]
        )
        >= max(2, len(words_of(s)) // 2)
    )

    metrics: Dict[str, float] = {
        "mean_sentence_words": round(statistics.mean(lengths), 2),
        "median_sentence_words": float(statistics.median(lengths)),
        "sentence_words_stdev": round(stdev, 2),
        # Variance relative to mean. Length-invariant, so an 80-word catalogue card and
        # a 900-word landing page can be held to the same rhythm standard.
        "sentence_words_cv": round(stdev / statistics.mean(lengths), 3),
        "p10_sentence_words": pct(0.10),
        "p90_sentence_words": pct(0.90),
        "min_sentence_words": min(lengths),
        "max_sentence_words": max(lengths),
        "short_sentence_ratio": round(sum(1 for l in lengths if l <= 6) / len(lengths), 3),
        "long_sentence_ratio": round(sum(1 for l in lengths if l >= 25) / len(lengths), 3),
        "em_dash_per_1000": per_thousand(text.count("\u2014") + text.count(" -- "), total_words),
        "colon_per_1000": per_thousand(text.count(":"), total_words),
        "semicolon_per_1000": per_thousand(text.count(";"), total_words),
        "question_per_1000": per_thousand(text.count("?"), total_words),
        "exclamation_per_1000": per_thousand(text.count("!"), total_words),
        "parenthetical_per_1000": per_thousand(text.count("("), total_words),
        "contractions_per_100": per_hundred(len(CONTRACTIONS.findall(text)), total_words),
        "second_person_per_100": per_hundred(len(SECOND_PERSON.findall(text)), total_words),
        "first_person_plural_per_100": per_hundred(len(FIRST_PLURAL.findall(text)), total_words),
        "hedges_per_100": per_hundred(len(HEDGES.findall(text)), total_words),
        "ly_adverbs_per_100": per_hundred(len(LY_ADVERB.findall(text)), total_words),
        "passive_hint_per_100": per_hundred(len(PASSIVE_HINT.findall(text)), total_words),
        "spec_tokens_per_100": per_hundred(len(SPEC_TOKEN.findall(text)), total_words),
        "tech_terms_per_100": per_hundred(len(tech_terms), total_words),
        "metaphor_per_1000": per_thousand(metaphor_hits, total_words),
        "imperative_opening_ratio": round(imperative_openers / len(sentences), 3),
        "headline_title_case_ratio": (
            round(title_case / len(headline_like), 3) if headline_like else 0.0
        ),
    }

    rules = load_rules(table_path)
    lowered_text = text.lower()
    corpus_counts = Counter(w.lower() for w in word_list)

    # A "banned" word the brand actually uses repeatedly is not a banned word.
    # It is a voice signature, and flagging it makes the agent fight the brand.
    protected = {p.lower() for p in rules.protected}
    reclaimed: List[Dict[str, object]] = []
    enforce: List[str] = []
    soft: List[str] = []
    for term, _fix in rules.words:
        occurrences = len(re.findall(r"\b%s\b" % re.escape(term.lower()), lowered_text))
        if occurrences >= 2:
            # Used repeatedly on purpose: this is voice, not slop. Never flag it.
            protected.add(term.lower())
            reclaimed.append({"term": term, "corpus_occurrences": occurrences})
        elif occurrences == 1:
            # Used once. Not a habit, so it still needs justifying — but blocking a word
            # that appears in the brand's own hero would make the linter untrustworthy.
            soft.append(term)
            enforce.append(term)
        else:
            enforce.append(term)

    distinctive = [
        {"term": term, "count": count}
        for term, count in corpus_counts.most_common(120)
        if term not in STOPWORDS and count >= 2 and len(term) > 3
    ][:20]

    codex = {
        "codex_version": 1,
        "generated_from": {
            # Relative to the skill directory, so the artefact is identical no matter
            # which directory the extractor was invoked from.
            "sample_dir": os.path.relpath(os.path.abspath(sample_dir), SKILL_DIR),
            "files": [{"file": d["file"], "source": d["source"]} for d in docs],
            "total_words": total_words,
            "total_sentences": len(sentences),
        },
        "tone_descriptors": tone_descriptors(metrics),
        "metrics": metrics,
        "jargon_tolerance": jargon_label(metrics["tech_terms_per_100"]),
        "metaphor_frequency": metaphor_label(metrics["metaphor_per_1000"]),
        "capitalization": (
            "Title Case headlines"
            if metrics["headline_title_case_ratio"] >= 0.5
            else "sentence case headlines"
        ),
        "signature_phrases": signature_phrases(word_list),
        "distinctive_terms": distinctive,
        "protected_terms": sorted(protected),
        "reclaimed_from_banned_list": reclaimed,
        "banned_phrases": enforce,
        "soft_banned_phrases": soft,
        "gates": {
            "_comment": (
                "Thresholds the linter enforces. Derived from the corpus, deliberately "
                "loosened so real brand copy passes its own test."
            ),
            "max_mean_sentence_words": round(
                max(metrics["mean_sentence_words"] * 1.35, 18.0), 1
            ),
            "min_sentence_words_cv": round(max(metrics["sentence_words_cv"] * 0.8, 0.45), 3),
            "min_short_sentence_ratio": round(
                max(metrics["short_sentence_ratio"] * 0.5, 0.10), 3
            ),
            "min_spec_tokens_per_100": round(
                max(metrics["spec_tokens_per_100"] * 0.6, 1.0), 2
            ),
            "max_hedges_per_100": round(max(metrics["hedges_per_100"] * 1.5, 0.6), 2),
            "max_ly_adverbs_per_100": round(
                max(metrics["ly_adverbs_per_100"] * 1.4, 1.8), 2
            ),
            "max_em_dash_per_1000": round(max(metrics["em_dash_per_1000"] * 2.0, 8.0), 2),
            "max_passive_hint_per_100": round(
                max(metrics["passive_hint_per_100"] * 1.5, 1.5), 2
            ),
            "max_protected_term_repeats": 2,
            "required_angles": ["logic", "pain", "social proof"],
            "max_angle_overlap": 0.5,
            "min_score_to_pass": 80,
        },
    }
    return codex


def print_summary(codex: Dict[str, object]) -> None:
    meta = codex["generated_from"]
    metrics = codex["metrics"]
    print("Voice codex — %d words, %d sentences, %d files"
          % (meta["total_words"], meta["total_sentences"], len(meta["files"])))
    print("Tone: " + "; ".join(codex["tone_descriptors"]))
    print("Sentence words: mean %.1f, stdev %.1f, band %d–%d"
          % (metrics["mean_sentence_words"], metrics["sentence_words_stdev"],
             metrics["p10_sentence_words"], metrics["p90_sentence_words"]))
    print("Jargon tolerance: %s" % codex["jargon_tolerance"])
    print("Metaphor: %s" % codex["metaphor_frequency"])
    print("Capitalization: %s" % codex["capitalization"])
    print("Protected (never flag): %s" % ", ".join(codex["protected_terms"]))
    if codex["reclaimed_from_banned_list"]:
        print("Reclaimed from banned list (brand uses these on purpose): %s"
              % ", ".join(r["term"] for r in codex["reclaimed_from_banned_list"]))
    print("Signature phrases: %s"
          % ", ".join('"%s" x%d' % (p["phrase"], p["count"])
                      for p in codex["signature_phrases"][:6]))
    print("Enforced banned phrases: %d" % len(codex["banned_phrases"]))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", required=True, help="directory of verbatim copy samples")
    parser.add_argument("--out", help="path to write voice-codex-<brand>.json")
    parser.add_argument("--table", help="path to buzzword-replacement-table.md")
    parser.add_argument("--print", dest="do_print", action="store_true",
                        help="print the human summary")
    args = parser.parse_args()

    codex = build_codex(args.samples, args.table)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            json.dump(codex, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        print("wrote %s" % args.out)
    if args.do_print or not args.out:
        print_summary(codex)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
