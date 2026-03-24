"""Tests for the legal citation parser."""

from legal_mcp.src.citation_parser import parse_citation


def test_supreme_court_citation():
    results = parse_citation("347 U.S. 483 (1954)")
    assert len(results) == 1
    c = results[0]
    assert c.volume == "347"
    assert c.reporter == "U.S."
    assert c.page == "483"
    assert c.year == "1954"


def test_circuit_court_citation():
    results = parse_citation("42 F.3d 1421 (D.C. Cir. 1994)")
    assert len(results) == 1
    c = results[0]
    assert c.volume == "42"
    assert c.reporter == "F.3d"
    assert c.page == "1421"
    assert c.court == "D.C. Cir."
    assert c.year == "1994"


def test_multiple_citations():
    text = "See Brown v. Board, 347 U.S. 483 (1954); Shelby County v. Holder, 570 U.S. 529 (2013)."
    results = parse_citation(text)
    assert len(results) == 2
    assert results[0].page == "483"
    assert results[1].page == "529"


def test_no_citations():
    results = parse_citation("This text has no legal citations.")
    assert len(results) == 0


def test_pin_cite():
    results = parse_citation("347 U.S. 483, 495 (1954)")
    assert len(results) == 1
    assert results[0].pin_cite == "495"
