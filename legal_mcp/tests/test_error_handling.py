"""Tests for API client error handling."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
from legal_mcp.src import courtlistener, clio, pacer


def _make_mock_client(side_effect=None, status_code=None):
    """Create a mock httpx.AsyncClient that raises the given error."""
    mock_client = MagicMock()
    if side_effect:
        mock_client.get = AsyncMock(side_effect=side_effect)
    elif status_code:
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.raise_for_status = MagicMock(
            side_effect=httpx.HTTPStatusError(
                f"{status_code}", request=MagicMock(), response=mock_response
            )
        )
        mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    return mock_client


# --- CourtListener Error Handling ---

@pytest.mark.asyncio
async def test_courtlistener_timeout():
    mock = _make_mock_client(side_effect=httpx.TimeoutException("timed out"))
    with patch("httpx.AsyncClient", return_value=mock):
        with pytest.raises(ConnectionError, match="CourtListener.*timed out"):
            await courtlistener.search_opinions(query="test")


@pytest.mark.asyncio
async def test_courtlistener_401():
    mock = _make_mock_client(status_code=401)
    with patch("httpx.AsyncClient", return_value=mock):
        with pytest.raises(PermissionError, match="COURTLISTENER_TOKEN"):
            await courtlistener.search_opinions(query="test")


@pytest.mark.asyncio
async def test_courtlistener_429():
    mock = _make_mock_client(status_code=429)
    with patch("httpx.AsyncClient", return_value=mock):
        with pytest.raises(ConnectionError, match="rate limit"):
            await courtlistener.search_opinions(query="test")


@pytest.mark.asyncio
async def test_courtlistener_connection_error():
    mock = _make_mock_client(side_effect=httpx.ConnectError("refused"))
    with patch("httpx.AsyncClient", return_value=mock):
        with pytest.raises(ConnectionError, match="internet connection"):
            await courtlistener.search_opinions(query="test")


# --- Clio Error Handling ---

@pytest.mark.asyncio
async def test_clio_missing_token():
    with patch.object(clio, "CLIO_TOKEN", ""):
        with pytest.raises(ValueError, match="CLIO_TOKEN"):
            await clio.search_contacts(query="test")


@pytest.mark.asyncio
async def test_clio_timeout():
    mock = _make_mock_client(side_effect=httpx.TimeoutException("timed out"))
    with patch("httpx.AsyncClient", return_value=mock), \
         patch.object(clio, "CLIO_TOKEN", "valid-token"):
        with pytest.raises(ConnectionError, match="Clio.*timed out"):
            await clio.search_contacts(query="test")


# --- PACER Error Handling ---

@pytest.mark.asyncio
async def test_pacer_missing_credentials():
    pacer._token_cache["token"] = None
    with patch.object(pacer, "PACER_USERNAME", ""), \
         patch.object(pacer, "PACER_PASSWORD", ""):
        with pytest.raises(ValueError, match="PACER"):
            await pacer.search_cases(case_name="test")
