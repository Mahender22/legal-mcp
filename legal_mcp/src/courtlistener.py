"""CourtListener API client for searching US case law."""

import httpx
from typing import Optional
from .config import COURTLISTENER_API_URL, COURTLISTENER_TOKEN


async def _get_headers() -> dict:
    headers = {"Content-Type": "application/json"}
    if COURTLISTENER_TOKEN:
        headers["Authorization"] = f"Token {COURTLISTENER_TOKEN}"
    return headers


async def _request(method: str, url: str, **kwargs) -> dict:
    """Make HTTP request with helpful error handling."""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await getattr(client, method)(url, headers=await _get_headers(), **kwargs)
            resp.raise_for_status()
            return resp.json()
    except httpx.TimeoutException:
        raise ConnectionError(
            "CourtListener API timed out. The service may be temporarily unavailable. "
            "Try again in a few seconds."
        )
    except httpx.HTTPStatusError as e:
        status = e.response.status_code
        if status == 401:
            raise PermissionError(
                "CourtListener authentication failed. Check your COURTLISTENER_TOKEN "
                "environment variable. Get a free token at https://www.courtlistener.com/sign-in/"
            )
        elif status == 429:
            raise ConnectionError(
                "CourtListener rate limit exceeded. Wait a moment and try again. "
                "Set COURTLISTENER_TOKEN for higher rate limits."
            )
        raise ConnectionError(f"CourtListener API error (HTTP {status}): {e}")
    except httpx.ConnectError:
        raise ConnectionError(
            "Cannot connect to CourtListener. Check your internet connection."
        )


async def search_opinions(
    query: str,
    court: Optional[str] = None,
    date_after: Optional[str] = None,
    date_before: Optional[str] = None,
    citation: Optional[str] = None,
    page: int = 1,
) -> dict:
    """Search CourtListener for court opinions."""
    from . import config
    if getattr(config, "DEMO_MODE", False):
        from .demo_data import get_demo_search_results
        return get_demo_search_results(query)

    params = {"type": "o", "q": query}
    if court:
        params["court"] = court
    if date_after:
        params["filed_after"] = date_after
    if date_before:
        params["filed_before"] = date_before
    if citation:
        params["citation"] = citation

    return await _request("get", f"{COURTLISTENER_API_URL}/search/", params=params)


async def get_opinion(opinion_id: int) -> dict:
    """Get a specific opinion by ID from CourtListener."""
    from . import config
    if getattr(config, "DEMO_MODE", False):
        from .demo_data import get_demo_opinion
        return get_demo_opinion(opinion_id)

    return await _request("get", f"{COURTLISTENER_API_URL}/opinions/{opinion_id}/")


async def get_cluster(cluster_id: int) -> dict:
    """Get an opinion cluster (group of related opinions) by ID."""
    return await _request("get", f"{COURTLISTENER_API_URL}/clusters/{cluster_id}/")


async def get_docket(docket_id: int) -> dict:
    """Get a docket (case record) by ID."""
    from . import config
    if getattr(config, "DEMO_MODE", False):
        from .demo_data import get_demo_docket
        return get_demo_docket(docket_id)

    return await _request("get", f"{COURTLISTENER_API_URL}/dockets/{docket_id}/")


async def get_citations(opinion_id: int) -> dict:
    """Get cases cited by a specific opinion."""
    from . import config
    if getattr(config, "DEMO_MODE", False):
        from .demo_data import get_demo_citations
        return get_demo_citations(opinion_id)

    return await _request(
        "get", f"{COURTLISTENER_API_URL}/opinions-cited/",
        params={"citing_opinion": opinion_id},
    )


async def get_cited_by(opinion_id: int) -> dict:
    """Get cases that cite a specific opinion (reverse citations)."""
    from . import config
    if getattr(config, "DEMO_MODE", False):
        from .demo_data import get_demo_cited_by
        return get_demo_cited_by(opinion_id)

    return await _request(
        "get", f"{COURTLISTENER_API_URL}/opinions-cited/",
        params={"cited_opinion": opinion_id},
    )


async def list_courts() -> dict:
    """List all available courts and their identifiers."""
    return await _request(
        "get", f"{COURTLISTENER_API_URL}/courts/",
        params={"page_size": 200},
    )
