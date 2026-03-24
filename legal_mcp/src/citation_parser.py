"""Legal citation parser for Bluebook-style citations."""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class ParsedCitation:
    volume: Optional[str] = None
    reporter: Optional[str] = None
    page: Optional[str] = None
    court: Optional[str] = None
    year: Optional[str] = None
    pin_cite: Optional[str] = None
    raw: str = ""

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}


# Common reporter abbreviations
REPORTERS = {
    "U.S.": "Supreme Court",
    "S. Ct.": "Supreme Court",
    "L. Ed.": "Supreme Court",
    "L. Ed. 2d": "Supreme Court",
    "F.2d": "Federal Circuit Courts",
    "F.3d": "Federal Circuit Courts",
    "F.4th": "Federal Circuit Courts",
    "F. Supp.": "Federal District Courts",
    "F. Supp. 2d": "Federal District Courts",
    "F. Supp. 3d": "Federal District Courts",
    "F.R.D.": "Federal Rules Decisions",
    "B.R.": "Bankruptcy Reporter",
    "A.2d": "Atlantic Reporter",
    "A.3d": "Atlantic Reporter",
    "N.E.2d": "North Eastern Reporter",
    "N.E.3d": "North Eastern Reporter",
    "N.W.2d": "North Western Reporter",
    "P.2d": "Pacific Reporter",
    "P.3d": "Pacific Reporter",
    "S.E.2d": "South Eastern Reporter",
    "S.W.2d": "South Western Reporter",
    "S.W.3d": "South Western Reporter",
    "So. 2d": "Southern Reporter",
    "So. 3d": "Southern Reporter",
    "Cal. Rptr.": "California Reporter",
    "N.Y.S.2d": "New York Supplement",
    "N.Y.S.3d": "New York Supplement",
}

# Regex pattern for standard Bluebook citations: Volume Reporter Page (Court Year)
CITATION_PATTERN = re.compile(
    r"(\d+)\s+"
    r"((?:U\.S\.|S\.\s*Ct\.|L\.\s*Ed\.(?:\s*2d)?|F\.(?:2d|3d|4th|R\.D\.)|"
    r"F\.\s*Supp\.(?:\s*(?:2d|3d))?|B\.R\.|"
    r"[A-Z]\.(?:[A-Z]\.)?(?:\s*(?:2d|3d))?|"
    r"(?:Cal|N\.Y\.S|So)\.\s*(?:Rptr|2d|3d)\.?))"
    r"\s+(\d+)"
    r"(?:,\s*(\d+))?"
    r"(?:\s*\(([^)]+)\))?"
)


def parse_citation(text: str) -> list[ParsedCitation]:
    """Parse legal citations from text.

    Handles standard Bluebook format: Volume Reporter Page (Court Year)
    Examples:
        - 347 U.S. 483 (1954) -> Brown v. Board
        - 570 U.S. 529 (2013) -> Shelby County v. Holder
        - 42 F.3d 1421 (D.C. Cir. 1994)
    """
    results = []
    for match in CITATION_PATTERN.finditer(text):
        volume, reporter, page, pin_cite, paren = match.groups()
        court = None
        year = None
        if paren:
            year_match = re.search(r"\d{4}", paren)
            if year_match:
                year = year_match.group()
                court_str = paren[:year_match.start()].strip().rstrip(",").strip()
                if court_str:
                    court = court_str

        results.append(ParsedCitation(
            volume=volume,
            reporter=reporter.strip(),
            page=page,
            court=court,
            year=year,
            pin_cite=pin_cite,
            raw=match.group(0),
        ))

    return results


def format_citation(citation: ParsedCitation) -> str:
    """Format a parsed citation back to Bluebook style."""
    parts = [citation.volume, citation.reporter, citation.page]
    if citation.pin_cite:
        parts.append(f", {citation.pin_cite}")
    paren_parts = []
    if citation.court:
        paren_parts.append(citation.court)
    if citation.year:
        paren_parts.append(citation.year)
    if paren_parts:
        parts.append(f"({' '.join(paren_parts)})")
    return " ".join(parts)
