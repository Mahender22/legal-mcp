"""Tests for CourtListener API client."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from legal_mcp.src import courtlistener


def _make_mock_client(response_data):
    """Create a properly mocked httpx.AsyncClient context manager."""
    mock_response = MagicMock()
    mock_response.json.return_value = response_data
    mock_response.raise_for_status = MagicMock()

    mock_client = MagicMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    return mock_client


@pytest.mark.asyncio
async def test_search_opinions_builds_params():
    mock_client = _make_mock_client({"count": 1, "results": [{"caseName": "Test v. Case"}]})

    with patch("httpx.AsyncClient", return_value=mock_client):
        result = await courtlistener.search_opinions(
            query="test query",
            court="scotus",
            date_after="2020-01-01",
        )

        assert result["count"] == 1
        call_kwargs = mock_client.get.call_args
        params = call_kwargs.kwargs.get("params") or call_kwargs[1].get("params")
        assert params["q"] == "test query"
        assert params["court"] == "scotus"
        assert params["filed_after"] == "2020-01-01"
        assert params["type"] == "o"


@pytest.mark.asyncio
async def test_search_opinions_no_filters():
    mock_client = _make_mock_client({"count": 0, "results": []})

    with patch("httpx.AsyncClient", return_value=mock_client):
        result = await courtlistener.search_opinions(query="anything")

        call_kwargs = mock_client.get.call_args
        params = call_kwargs.kwargs.get("params") or call_kwargs[1].get("params")
        assert "court" not in params
        assert "filed_after" not in params


@pytest.mark.asyncio
async def test_get_opinion():
    mock_client = _make_mock_client({"id": 123, "type": "lead", "plain_text": "Opinion text"})

    with patch("httpx.AsyncClient", return_value=mock_client):
        result = await courtlistener.get_opinion(123)
        assert result["id"] == 123


@pytest.mark.asyncio
async def test_get_docket():
    mock_client = _make_mock_client({"case_name": "Smith v. Jones", "court": "scotus"})

    with patch("httpx.AsyncClient", return_value=mock_client):
        result = await courtlistener.get_docket(456)
        assert result["case_name"] == "Smith v. Jones"


@pytest.mark.asyncio
async def test_list_courts():
    mock_client = _make_mock_client({"results": [{"id": "scotus", "short_name": "Supreme Court"}]})

    with patch("httpx.AsyncClient", return_value=mock_client):
        result = await courtlistener.list_courts()
        assert len(result["results"]) == 1
        assert result["results"][0]["id"] == "scotus"
