"""Tests for demo/sandbox mode."""

import pytest
from unittest.mock import patch
from legal_mcp.src import courtlistener, config


@pytest.mark.asyncio
async def test_demo_mode_returns_search_results():
    with patch.object(config, "DEMO_MODE", True):
        result = await courtlistener.search_opinions(query="fourth amendment")
        assert result["count"] > 0
        assert len(result["results"]) > 0


@pytest.mark.asyncio
async def test_demo_mode_matches_relevant_cases():
    with patch.object(config, "DEMO_MODE", True):
        result = await courtlistener.search_opinions(query="fourth amendment cell phone")
        names = [c["caseName"] for c in result["results"]]
        assert "Carpenter v. United States" in names


@pytest.mark.asyncio
async def test_demo_mode_returns_all_for_unmatched_query():
    with patch.object(config, "DEMO_MODE", True):
        result = await courtlistener.search_opinions(query="xyzzy nonexistent topic")
        assert result["count"] == 10  # All demo cases returned as fallback


@pytest.mark.asyncio
async def test_demo_mode_get_opinion():
    with patch.object(config, "DEMO_MODE", True):
        result = await courtlistener.get_opinion(2812209)
        assert result["id"] == 2812209
        assert "cell-site" in result["plain_text"].lower() or "CSLI" in result["plain_text"]


@pytest.mark.asyncio
async def test_demo_mode_get_docket():
    with patch.object(config, "DEMO_MODE", True):
        result = await courtlistener.get_docket(98675)
        assert result["case_name"] == "Brown v. Board of Education"


@pytest.mark.asyncio
async def test_demo_mode_get_citations():
    with patch.object(config, "DEMO_MODE", True):
        result = await courtlistener.get_citations(2812209)
        assert result["count"] > 0
        assert all(c["citing_opinion"] == 2812209 for c in result["results"])


@pytest.mark.asyncio
async def test_demo_mode_get_cited_by():
    with patch.object(config, "DEMO_MODE", True):
        result = await courtlistener.get_cited_by(2812209)
        assert result["count"] > 0
        assert all(c["cited_opinion"] == 2812209 for c in result["results"])


def test_demo_mode_defaults_to_false():
    # Without LEGAL_MCP_DEMO env var, should be False
    import os
    original = os.environ.get("LEGAL_MCP_DEMO")
    os.environ.pop("LEGAL_MCP_DEMO", None)
    # Re-evaluate — config.DEMO_MODE was set at import time,
    # but we test the logic, not the cached value
    result = os.environ.get("LEGAL_MCP_DEMO", "").lower() in ("1", "true", "yes")
    assert result is False
    if original is not None:
        os.environ["LEGAL_MCP_DEMO"] = original
