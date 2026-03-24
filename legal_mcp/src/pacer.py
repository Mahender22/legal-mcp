"""PACER API client for federal court filings."""

import httpx
from typing import Optional
from .config import PACER_USERNAME, PACER_PASSWORD

PACER_LOGIN_URL = "https://pacer.login.uscourts.gov/services/cso-auth"
PACER_SEARCH_URL = "https://pcl.uscourts.gov/pcl-public-api/rest"

_token_cache: dict = {"token": None}


async def _authenticate() -> str:
    """Authenticate with PACER and get a session token."""
    if _token_cache["token"]:
        return _token_cache["token"]

    if not PACER_USERNAME or not PACER_PASSWORD:
        raise ValueError(
            "PACER credentials not set. Set PACER_USERNAME and PACER_PASSWORD "
            "environment variables. Register at https://pacer.uscourts.gov"
        )

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            PACER_LOGIN_URL,
            json={"loginId": PACER_USERNAME, "password": PACER_PASSWORD},
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        resp.raise_for_status()
        data = resp.json()
        token = data.get("nextGenCSO", data.get("loginResult", ""))
        _token_cache["token"] = token
        return token


async def _get_headers() -> dict:
    token = await _authenticate()
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-NEXT-GEN-CSO": token,
    }


async def search_cases(
    case_name: Optional[str] = None,
    case_number: Optional[str] = None,
    court_id: Optional[str] = None,
    date_filed_from: Optional[str] = None,
    date_filed_to: Optional[str] = None,
    nature_of_suit: Optional[str] = None,
    page: int = 1,
) -> dict:
    """Search PACER for federal court cases.

    Args:
        case_name: Party name or case title to search
        case_number: Specific case number
        court_id: Court identifier (e.g., 'nysd' for Southern District of NY)
        date_filed_from: Start date (MM/DD/YYYY)
        date_filed_to: End date (MM/DD/YYYY)
        nature_of_suit: Nature of suit code
        page: Page number for results
    """
    params = {"pageNumber": page}
    if case_name:
        params["caseName"] = case_name
    if case_number:
        params["caseNumber"] = case_number
    if court_id:
        params["courtId"] = court_id
    if date_filed_from:
        params["dateFiledFrom"] = date_filed_from
    if date_filed_to:
        params["dateFiledTo"] = date_filed_to
    if nature_of_suit:
        params["natureOfSuit"] = nature_of_suit

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"{PACER_SEARCH_URL}/cases",
            params=params,
            headers=await _get_headers(),
        )
        resp.raise_for_status()
        return resp.json()


async def get_case(case_id: str, court_id: str) -> dict:
    """Get details of a specific PACER case.

    Args:
        case_id: The PACER case ID
        court_id: The court identifier
    """
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"{PACER_SEARCH_URL}/cases/{case_id}",
            params={"courtId": court_id},
            headers=await _get_headers(),
        )
        resp.raise_for_status()
        return resp.json()


async def get_docket_entries(
    case_id: str,
    court_id: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    page: int = 1,
) -> dict:
    """Get docket entries (filings) for a PACER case.

    Args:
        case_id: The PACER case ID
        court_id: The court identifier
        date_from: Start date filter (MM/DD/YYYY)
        date_to: End date filter (MM/DD/YYYY)
        page: Page number
    """
    params = {"courtId": court_id, "pageNumber": page}
    if date_from:
        params["dateFrom"] = date_from
    if date_to:
        params["dateTo"] = date_to

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"{PACER_SEARCH_URL}/cases/{case_id}/docket-entries",
            params=params,
            headers=await _get_headers(),
        )
        resp.raise_for_status()
        return resp.json()
