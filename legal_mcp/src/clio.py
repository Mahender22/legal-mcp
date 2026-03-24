"""Clio API client for legal practice management."""

import httpx
from typing import Optional
from .config import CLIO_API_URL, CLIO_TOKEN


async def _get_headers() -> dict:
    headers = {"Content-Type": "application/json"}
    if CLIO_TOKEN:
        headers["Authorization"] = f"Bearer {CLIO_TOKEN}"
    return headers


async def _get(endpoint: str, params: Optional[dict] = None) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"{CLIO_API_URL}/{endpoint}",
            params=params or {},
            headers=await _get_headers(),
        )
        resp.raise_for_status()
        return resp.json()


async def search_contacts(
    query: Optional[str] = None,
    contact_type: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
) -> dict:
    """Search contacts in Clio.

    Args:
        query: Search term (name, email, phone)
        contact_type: 'Person' or 'Company'
        page: Page number
        limit: Results per page
    """
    params = {"page": page, "limit": limit, "fields": "id,name,type,email_addresses,phone_numbers"}
    if query:
        params["query"] = query
    if contact_type:
        params["type"] = contact_type
    return await _get("contacts.json", params)


async def get_contact(contact_id: int) -> dict:
    """Get a specific contact by ID.

    Args:
        contact_id: The Clio contact ID
    """
    params = {"fields": "id,name,type,email_addresses,phone_numbers,addresses,company,custom_field_values"}
    return await _get(f"contacts/{contact_id}.json", params)


async def search_matters(
    query: Optional[str] = None,
    status: Optional[str] = None,
    client_id: Optional[int] = None,
    page: int = 1,
    limit: int = 20,
) -> dict:
    """Search matters (cases) in Clio.

    Args:
        query: Search term (matter number, description)
        status: 'Open', 'Closed', or 'Pending'
        client_id: Filter by client contact ID
        page: Page number
        limit: Results per page
    """
    params = {
        "page": page,
        "limit": limit,
        "fields": "id,display_number,description,status,client,practice_area,open_date,close_date",
    }
    if query:
        params["query"] = query
    if status:
        params["status"] = status
    if client_id:
        params["client_id"] = client_id
    return await _get("matters.json", params)


async def get_matter(matter_id: int) -> dict:
    """Get a specific matter (case) by ID.

    Args:
        matter_id: The Clio matter ID
    """
    params = {
        "fields": (
            "id,display_number,description,status,client,practice_area,"
            "responsible_attorney,open_date,close_date,billing_method,"
            "statute_of_limitations,custom_field_values"
        )
    }
    return await _get(f"matters/{matter_id}.json", params)


async def get_time_entries(
    matter_id: Optional[int] = None,
    user_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
) -> dict:
    """Get time entries from Clio.

    Args:
        matter_id: Filter by matter ID
        user_id: Filter by user (attorney) ID
        date_from: Start date filter (YYYY-MM-DD)
        date_to: End date filter (YYYY-MM-DD)
        page: Page number
        limit: Results per page
    """
    params = {
        "page": page,
        "limit": limit,
        "fields": "id,date,quantity,note,matter,user,activity_description,total",
    }
    if matter_id:
        params["matter_id"] = matter_id
    if user_id:
        params["user_id"] = user_id
    if date_from:
        params["date_from"] = date_from
    if date_to:
        params["date_to"] = date_to
    return await _get("activities.json", params)


async def get_tasks(
    matter_id: Optional[int] = None,
    status: Optional[str] = None,
    assignee_id: Optional[int] = None,
    page: int = 1,
    limit: int = 20,
) -> dict:
    """Get tasks from Clio.

    Args:
        matter_id: Filter by matter ID
        status: 'Complete' or 'Incomplete'
        assignee_id: Filter by assigned user ID
        page: Page number
        limit: Results per page
    """
    params = {
        "page": page,
        "limit": limit,
        "fields": "id,name,description,status,due_at,matter,assignee,priority",
    }
    if matter_id:
        params["matter_id"] = matter_id
    if status:
        params["status"] = status
    if assignee_id:
        params["assignee_id"] = assignee_id
    return await _get("tasks.json", params)


async def get_documents(
    matter_id: Optional[int] = None,
    query: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
) -> dict:
    """Get documents from Clio.

    Args:
        matter_id: Filter by matter ID
        query: Search term for document name
        page: Page number
        limit: Results per page
    """
    params = {
        "page": page,
        "limit": limit,
        "fields": "id,name,content_type,created_at,updated_at,matter,latest_document_version",
    }
    if matter_id:
        params["matter_id"] = matter_id
    if query:
        params["query"] = query
    return await _get("documents.json", params)


async def get_calendar_entries(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    matter_id: Optional[int] = None,
    page: int = 1,
    limit: int = 20,
) -> dict:
    """Get calendar entries from Clio.

    Args:
        date_from: Start date filter (YYYY-MM-DD)
        date_to: End date filter (YYYY-MM-DD)
        matter_id: Filter by matter ID
        page: Page number
        limit: Results per page
    """
    params = {
        "page": page,
        "limit": limit,
        "fields": "id,summary,description,start_at,end_at,location,matter,attendees",
    }
    if date_from:
        params["start_date_from"] = date_from
    if date_to:
        params["start_date_to"] = date_to
    if matter_id:
        params["matter_id"] = matter_id
    return await _get("calendar_entries.json", params)
