"""Shared text measurement used by the codex extractor and the copy linter.

Both tools must tokenize identically or the linter's gates will not match the
numbers they were calibrated against.
"""

from __future__ import annotations

import re
from typing import List

STOPWORDS = set(
    """a an the and or but if then than that this these those of to in on for with
    at by from as is are was were be been being am do does did doing have has had
    having it its it's you your yours we our ours us i me my they them their he she
    his her not no so such can could will would shall should may might must into
    over under about after before during while all any both each few more most other
    some only own same too very just now also here there when where who whom which
    what how why because up down out off again further once between against through
    above below""".split()
)

CONTRACTIONS = re.compile(r"\b\w+['\u2019](?:s|t|re|ve|ll|d|m)\b", re.IGNORECASE)
SECOND_PERSON = re.compile(r"\b(you|your|yours|yourself)\b", re.IGNORECASE)
FIRST_PLURAL = re.compile(r"\b(we|our|ours|us)\b", re.IGNORECASE)
HEDGES = re.compile(
    r"\b(can help|helps to|aims to|designed to|might|maybe|perhaps|somewhat|"
    r"fairly|quite|rather|arguably|potentially|hopefully|try to|attempt to)\b",
    re.IGNORECASE,
)
LY_ADVERB = re.compile(r"\b\w{4,}ly\b", re.IGNORECASE)
PASSIVE_HINT = re.compile(
    r"\b(is|are|was|were|be|been|being)\s+\w+(ed|en)\b", re.IGNORECASE
)
SIMILE = re.compile(
    r"\b(like a|like the|as if|as though|think of it as|it's basically|"
    r"the way a|same way)\b",
    re.IGNORECASE,
)
METAPHOR_LEXICON = re.compile(
    r"\b(?:engine|blueprint|recipe|scaffold|skeleton|muscle|backbone|spine|"
    r"pipeline|rail|runway|flywheel|lever|compass|map|playbook|toolkit|"
    r"foundation|architecture|anatomy)s?\b",
    re.IGNORECASE,
)
TECH_TERM = re.compile(
    r"\b(?:api|sdk|cli|json|html|css|repo|deploy(?:ment)?|runtime|pipeline|"
    r"sandbox|render|shader|webgl|node|schema|endpoint|token|build|commit|"
    r"latency|throughput|cache|config|framework|component|export|import|"
    r"architecture)\w*\b",
    re.IGNORECASE,
)
SPEC_TOKEN = re.compile(
    r"(\d+(?:[.,]\d+)?\s?(?:%|x|k|m|bn|hrs?|hours?|mins?|days?|weeks?|months?)?"
    r"|\$\d[\d,.]*|v\d+(?:\.\d+)*|\d{4})",
    re.IGNORECASE,
)
BASE_VERB_OPENERS = set(
    """get build ship learn start join master run open read write make take use
    stop skip lock pick see watch download copy paste steal bring keep cut add
    fix send drop hit try test deploy export import study adapt secure claim
    grab install follow check book reserve save switch swap
    create delete choose select share invite upload connect reconnect retry
    sign confirm rename duplicate move remove archive restore publish upgrade
    downgrade cancel close edit update refresh request verify view name
    describe allow enable disable set finish continue find search filter sort
    tag assign approve reject pay buy order track print scan apply redeem
    resend replace clear undo repeat contact call email reply forward attach
    turn link unlink import review accept decline schedule reschedule
    ask tell show give press tap click swipe pull push begin resume pause""".split()
)


def blank_comments(raw: str) -> str:
    """Blank out HTML comments while preserving every byte offset and line break.

    Notes to the author are not copy, so they must not be linted — but line numbers
    in the report have to keep pointing at the real file.
    """
    def blanker(match: "re.Match") -> str:
        return re.sub(r"[^\n]", " ", match.group(0))

    return re.sub(r"<!--.*?-->", blanker, raw, flags=re.DOTALL)


def unwrap(text: str) -> str:
    """Join hard-wrapped continuation lines back into single logical lines.

    Without this, a paragraph wrapped at 78 columns measures as six short
    sentences and the rhythm statistics are meaningless.
    """
    out: List[str] = []
    for line in text.split("\n"):
        stripped = line.strip()
        if (
            out
            and out[-1]
            and stripped
            and not re.search(r"[.!?:;\u2014]$", out[-1])
            and re.match(r"[a-z0-9(\"'\u201c]", stripped)
        ):
            out[-1] = out[-1] + " " + stripped
        else:
            out.append(stripped)
    return "\n".join(out)


def drop_headings(text: str) -> str:
    """Remove heading lines. An em dash in "## Angle 1 — Logic" is a label, not a habit."""
    return "\n".join(
        line for line in text.split("\n") if not re.match(r"^\s{0,3}#{1,6}\s", line)
    )


def strip_markup(text: str) -> str:
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL)
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s{0,3}[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"[*_]{1,3}([^*_]+)[*_]{1,3}", r"\1", text)
    return text


def split_sentences(text: str) -> List[str]:
    # Hard line breaks are boundaries: headlines and CTAs rarely end in a period.
    chunks = [c.strip() for c in re.split(r"\n{1,}", unwrap(text)) if c.strip()]
    sentences: List[str] = []
    for chunk in chunks:
        parts = re.split(r"(?<=[.!?])[\s\u00a0]+(?=[\"'\u201c(A-Z0-9])", chunk)
        for part in parts:
            cleaned = part.strip(" \t\u2014-")
            if len(re.findall(r"[A-Za-z]", cleaned)) >= 2:
                sentences.append(cleaned)
    return sentences


def words_of(text: str) -> List[str]:
    return re.findall(r"[A-Za-z][A-Za-z'\u2019\-]*", text)


def content_words(text: str) -> List[str]:
    return [w.lower() for w in words_of(text) if w.lower() not in STOPWORDS and len(w) > 2]


# Buried verbs: a verb turned into a noun. -ity and a bare -al are deliberately excluded
# because they catch adjectives ("critical") and legal nouns with no verb to restore
# ("liability"); the -al nominalizations that do matter are listed explicitly instead.
NOMINALIZATION = re.compile(
    r"\b(?:\w{4,}(?:tion|sion|ment|ance|ence|ancy|ency)"
    r"|renewals?|approvals?|removals?|referrals?|dismissals?|proposals?"
    r"|withdrawals?|disposals?|refusals?|reversals?|deferrals?)s?\b",
    re.IGNORECASE,
)
# Ordinary nouns that end in a nominalizing suffix but bury no verb.
NOMINALIZATION_ALLOW = {
    "information", "question", "section", "option", "condition", "position",
    "solution", "situation", "attention", "portion", "version", "person",
    "moment", "document", "instrument", "element", "equipment", "environment",
    "government", "department", "argument", "component", "content", "percent",
    "experience", "audience", "science", "sentence", "difference", "reference",
    "evidence", "confidence", "distance", "balance", "chance", "finance",
    "insurance", "circumstance", "consequence", "sequence", "silence",
    "presence", "absence", "licence", "license", "residence", "occurrence",
    "emergency", "agency", "currency", "frequency", "tendency", "distinction",
}


def syllables(word: str) -> int:
    """Vowel-group heuristic. Good enough for a reading-grade band, not for poetry."""
    word = re.sub(r"[^a-z]", "", word.lower())
    if not word:
        return 0
    if len(word) <= 3:
        return 1
    stripped = re.sub(r"(?:[^laeiouy]es|[^laeiouy]e)$", "", word)
    stripped = re.sub(r"^y", "", stripped)
    count = len(re.findall(r"[aeiouy]{1,2}", stripped))
    return max(1, count)


def flesch_kincaid_grade(sentences: List[str], word_list: List[str]) -> float:
    """US school grade needed to read the text on the first pass."""
    if not sentences or not word_list:
        return 0.0
    total_syllables = sum(syllables(w) for w in word_list)
    words_per_sentence = len(word_list) / len(sentences)
    syllables_per_word = total_syllables / len(word_list)
    return round(0.39 * words_per_sentence + 11.8 * syllables_per_word - 15.59, 1)


def nominalizations(text: str) -> List[str]:
    """Verbs buried inside nouns: "make a determination" instead of "decide"."""
    return [
        m.group(0)
        for m in NOMINALIZATION.finditer(text)
        if m.group(0).lower().rstrip("s") not in NOMINALIZATION_ALLOW
        and m.group(0).lower() not in NOMINALIZATION_ALLOW
    ]


def per_thousand(count: int, total_words: int) -> float:
    if total_words == 0:
        return 0.0
    return round(count * 1000.0 / total_words, 2)


def per_hundred(count: int, total_words: int) -> float:
    if total_words == 0:
        return 0.0
    return round(count * 100.0 / total_words, 2)


def figurative_hits(text: str) -> List[str]:
    """Metaphor-lexicon matches that are not this register's literal technical nouns."""
    return [
        m.group(0)
        for m in METAPHOR_LEXICON.finditer(text)
        if not TECH_TERM.fullmatch(m.group(0))
    ]


def line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1
