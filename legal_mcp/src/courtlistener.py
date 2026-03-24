"""CourtListener API client for searching US case law."""

import httpx
from typing import Optional
from .config import COURTLISTENER_API_URL, COURTLISTENER_TOKEN


async def _get_headers() -> dict:
    headers = {"Content-Type": "application/json"}
    if COURTLISTENER_TOKEN:
        headers["Authorization"] = f"Token {COURTLISTENER_TOKEN}"
    return headers


async def search_opinions(
    query: str,
    court: Optional[str] = None,
    date_after: Optional[str] = None,
    date_before: Optional[str] = None,
    citation: Optional[str] = None,
    page: int = 1,
) -> dict:
    """Search CourtListener for court opinions.

    Args:
        query: Search terms (case name, legal concept, statute, etc.)
        court: Court filter (e.g., 'scotus', 'ca9', 'nysd')
        date_after: Filter opinions filed after this date (YYYY-MM-DD)
        date_before: Filter opinions filed before this date (YYYY-MM-DD)
        citation: Search by citation string
        page: Page number for pagination
    """
    params = {"type": "o", "q": query}
    if court:
        params["court"] = court
    if date_after:
        params["filed_after"] = date_after
    if date_before:
        params["filed_before"] = date_before
    if citation:
        params["citation"] = citation

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"{COURTLISTENER_API_URL}/search/",
            params=params,
            headers=await _get_headers(),
        )
        resp.raise_for_status()
        return resp.json()


async def get_opinion(opinion_id: int) -> dict:
    """Get a specific opinion by ID from CourtListener.

    Args:
        opinion_id: The CourtListener opinion ID
    """
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"{COURTLISTENER_API_URL}/opinions/{opinion_id}/",
            headers=await _get_headers(),
        )
        resp.raise_for_status()
        return resp.json()


async def get_cluster(cluster_id: int) -> dict:
    """Get an opinion cluster (group of related opinions) by ID.

    Args:
        cluster_id: The CourtListener cluster ID
    """
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"{COURTLISTENER_API_URL}/clusters/{cluster_id}/",
            headers=await _get_headers(),
        )
        resp.raise_for_status()
        return resp.json()


async def get_docket(docket_id: int) -> dict:
    """Get a docket (case record) by ID.

    Args:
        docket_id: The CourtListener docket ID
    """
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"{COURTLISTENER_API_URL}/dockets/{docket_id}/",
            headers=await _get_headers(),
        )
        resp.raise_for_status()
        return resp.json()


async def get_citations(opinion_id: int) -> dict:
    """Get cases cited by a specific opinion.

    Args:
        opinion_id: The CourtListener opinion ID to find citations for
    """
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"{COURTLISTENER_API_URL}/opinions-cited/",
            params={"citing_opinion": opinion_id},
            headers=await _get_headers(),
        )
        resp.raise_for_status()
        return resp.json()


async def get_cited_by(opinion_id: int) -> dict:
    """Get cases that cite a specific opinion (reverse citations).

    Args:
        opinion_id: The CourtListener opinion ID to find citing cases for
    """
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"{COURTLISTENER_API_URL}/opinions-cited/",
            params={"cited_opinion": opinion_id},
            headers=await _get_headers(),
        )
        resp.raise_for_status()
        return resp.json()


async def list_courts() -> dict:
    """List all available courts and their identifiers."""
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"{COURTLISTENER_API_URL}/courts/",
            params={"page_size": 200},
            headers=await _get_headers(),
        )
        resp.raise_for_status()
        return resp.json()
