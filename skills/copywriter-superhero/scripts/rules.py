"""Parses references/buzzword-replacement-table.md into machine rules.

The markdown table is the single source of truth. Editing the table changes the
linter, so the human-facing doc and the enforced rules can never drift apart.
"""

from __future__ import annotations

import os
import re
import sys
from typing import Dict, List, Optional, Tuple

DEFAULT_TABLE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "references",
    "buzzword-replacement-table.md",
)

_TABLE_A_HEADING = "table a"
_TABLE_B_HEADING = "table b"
_PROTECTED_HEADING = "protected terms"


def _unescape_cell(cell: str) -> str:
    return cell.replace("\\|", "|").strip()


def _split_row(line: str) -> Optional[List[str]]:
    stripped = line.strip()
    if not stripped.startswith("|"):
        return None
    # Split on unescaped pipes only.
    parts = re.split(r"(?<!\\)\|", stripped)
    cells = [_unescape_cell(p) for p in parts]
    # Leading/trailing pipes produce empty edge cells.
    if cells and cells[0] == "":
        cells = cells[1:]
    if cells and cells[-1] == "":
        cells = cells[:-1]
    if not cells:
        return None
    if all(re.fullmatch(r":?-{2,}:?", c or "-") for c in cells):
        return None  # separator row
    return cells


class Rules:
    def __init__(
        self,
        words: List[Tuple[str, str]],
        constructions: List[Tuple[str, str, str]],
        protected: List[str],
    ) -> None:
        self.words = words
        self.constructions = constructions
        self.protected = protected
        self._word_res: List[Tuple[re.Pattern, str, str]] = []
        for term, fix in words:
            self._word_res.append((self._word_pattern(term), term, fix))
        self._construction_res: List[Tuple[re.Pattern, str, str, str]] = []
        for pattern, why, fix in constructions:
            try:
                compiled = re.compile(pattern, re.IGNORECASE | re.DOTALL)
            except re.error as exc:
                print(
                    "warning: skipping invalid construction regex %r (%s)"
                    % (pattern, exc),
                    file=sys.stderr,
                )
                continue
            self._construction_res.append((compiled, pattern, why, fix))

    @staticmethod
    def _word_pattern(term: str) -> re.Pattern:
        escaped = re.escape(term)
        # Let a trailing period in "etc." match literally without demanding \b after it.
        lead = r"\b" if re.match(r"\w", term) else ""
        trail = r"\b" if re.search(r"\w$", term) else ""
        return re.compile(lead + escaped + trail, re.IGNORECASE)

    def word_hits(self, text: str, allow: Optional[List[str]] = None):
        allowed = {a.lower() for a in (allow or [])}
        for pattern, term, fix in self._word_res:
            if term.lower() in allowed:
                continue
            for match in pattern.finditer(text):
                yield term, fix, match.start(), match.group(0)

    def construction_hits(self, text: str):
        for compiled, pattern, why, fix in self._construction_res:
            for match in compiled.finditer(text):
                yield pattern, why, fix, match.start(), match.group(0)

    def replacement_for(self, term: str) -> str:
        for candidate, fix in self.words:
            if candidate.lower() == term.lower():
                return fix
        return ""


def load_rules(path: Optional[str] = None) -> Rules:
    path = path or DEFAULT_TABLE
    with open(path, "r", encoding="utf-8") as handle:
        lines = handle.readlines()

    section = None
    words: List[Tuple[str, str]] = []
    constructions: List[Tuple[str, str, str]] = []
    protected: List[str] = []

    for line in lines:
        heading = re.match(r"^#{2,3}\s+(.*)$", line.strip())
        if heading:
            title = heading.group(1).lower()
            if title.startswith(_TABLE_A_HEADING):
                section = "words"
            elif title.startswith(_TABLE_B_HEADING):
                section = "constructions"
            elif title.startswith(_PROTECTED_HEADING):
                section = "protected"
            else:
                section = None
            continue

        if section == "protected":
            # Only bare terms, so prose mentioning `some-file.json` is not protected.
            protected.extend(
                t for t in re.findall(r"`([^`]+)`", line)
                if re.fullmatch(r"[a-z][a-z0-9\-]*(?: [a-z0-9\-]+)?", t)
            )
            continue

        cells = _split_row(line)
        if not cells:
            continue
        header = cells[0].strip().lower()
        if header in ("banned", "regex"):
            continue
        if section == "words" and len(cells) >= 2 and cells[0]:
            words.append((cells[0], cells[1]))
        elif section == "constructions" and len(cells) >= 3 and cells[0]:
            pattern = cells[0].strip().strip("`")
            constructions.append((pattern, cells[1], cells[2]))

    if not words or not constructions:
        raise SystemExit(
            "error: parsed %d words and %d constructions from %s — table format broken"
            % (len(words), len(constructions), path)
        )

    return Rules(words=words, constructions=constructions, protected=protected)


def summary(rules: Rules) -> Dict[str, int]:
    return {
        "banned_words": len(rules.words),
        "banned_constructions": len(rules.constructions),
        "protected_terms": len(rules.protected),
    }


if __name__ == "__main__":
    loaded = load_rules(sys.argv[1] if len(sys.argv) > 1 else None)
    for key, value in summary(loaded).items():
        print("%s: %d" % (key, value))
