"""Legal MCP Server — US case law, citations, and practice management for AI assistants."""

from fastmcp import FastMCP
from typing import Optional
from . import courtlistener, clio, pacer
from .citation_parser import parse_citation, REPORTERS

mcp = FastMCP(
    name="Legal MCP Server",
    instructions=(
        "You are connected to a legal research MCP server that provides access to "
        "US case law via CourtListener, citation parsing, and legal research tools. "
        "Use these tools to find real case law, analyze citations, and assist with "
        "legal research. Always cite sources and note that this is for research "
        "purposes — not legal advice."
    ),
)


# --- Case Law Search Tools ---

@mcp.tool
async def search_case_law(
    query: str,
    court: Optional[str] = None,
    date_after: Optional[str] = None,
    date_before: Optional[str] = None,
) -> dict:
    """Search US case law for court opinions matching a query.

    Use this to find cases about specific legal topics, statutes, or concepts.

    Args:
        query: Legal search terms (e.g., "duty to mitigate breach of contract",
               "Fourth Amendment reasonable expectation of privacy")
        court: Optional court filter. Examples: 'scotus' (Supreme Court),
               'ca9' (9th Circuit), 'nysd' (Southern District of New York)
        date_after: Only show cases filed after this date (YYYY-MM-DD)
        date_before: Only show cases filed before this date (YYYY-MM-DD)
    """
    result = await courtlistener.search_opinions(
        query=query,
        court=court,
        date_after=date_after,
        date_before=date_before,
    )
    # Format results for readability
    cases = []
    for item in result.get("results", [])[:10]:
        cases.append({
            "case_name": item.get("caseName", "Unknown"),
            "court": item.get("court", "Unknown"),
            "date_filed": item.get("dateFiled", "Unknown"),
            "citation": item.get("citation", []),
            "snippet": item.get("snippet", ""),
            "opinion_id": item.get("id"),
            "cluster_id": item.get("cluster_id"),
            "absolute_url": f"https://www.courtlistener.com{item.get('absolute_url', '')}",
        })
    return {
        "total_results": result.get("count", 0),
        "cases": cases,
        "query": query,
    }


@mcp.tool
async def get_case_details(opinion_id: int) -> dict:
    """Get full details of a specific court opinion by its ID.

    Use this after search_case_law to get the full text and details of a case.

    Args:
        opinion_id: The opinion ID from a search result
    """
    opinion = await courtlistener.get_opinion(opinion_id)
    return {
        "id": opinion.get("id"),
        "type": opinion.get("type"),
        "html_with_citations": opinion.get("html_with_citations", "")[:5000],
        "plain_text": opinion.get("plain_text", "")[:5000],
        "download_url": opinion.get("download_url"),
        "cluster": opinion.get("cluster"),
        "author": opinion.get("author"),
        "joined_by": opinion.get("joined_by", []),
    }


@mcp.tool
async def get_case_record(docket_id: int) -> dict:
    """Get the full docket (case record) for a case.

    Includes parties, attorneys, judges, and procedural history.

    Args:
        docket_id: The docket ID from a case search result
    """
    docket = await courtlistener.get_docket(docket_id)
    return {
        "case_name": docket.get("case_name"),
        "court": docket.get("court"),
        "date_filed": docket.get("date_filed"),
        "date_terminated": docket.get("date_terminated"),
        "assigned_to": docket.get("assigned_to_str"),
        "referred_to": docket.get("referred_to_str"),
        "cause": docket.get("cause"),
        "nature_of_suit": docket.get("nature_of_suit"),
        "jury_demand": docket.get("jury_demand"),
        "docket_number": docket.get("docket_number"),
        "pacer_case_id": docket.get("pacer_case_id"),
        "absolute_url": f"https://www.courtlistener.com{docket.get('absolute_url', '')}",
    }


# --- Citation Tools ---

@mcp.tool
async def find_citing_cases(opinion_id: int) -> dict:
    """Find cases that cite a specific opinion (who cited this case later?).

    Use this to trace how a case has been used in subsequent rulings.

    Args:
        opinion_id: The opinion ID to find citing cases for
    """
    result = await courtlistener.get_cited_by(opinion_id)
    citations = []
    for item in result.get("results", [])[:20]:
        citations.append({
            "citing_opinion": item.get("citing_opinion"),
            "cited_opinion": item.get("cited_opinion"),
            "depth": item.get("depth"),
        })
    return {
        "total_citing_cases": result.get("count", 0),
        "citations": citations,
    }


@mcp.tool
async def find_cited_cases(opinion_id: int) -> dict:
    """Find cases that a specific opinion cites (what cases did this ruling rely on?).

    Use this to understand the legal foundation of a decision.

    Args:
        opinion_id: The opinion ID to find cited cases for
    """
    result = await courtlistener.get_citations(opinion_id)
    citations = []
    for item in result.get("results", [])[:20]:
        citations.append({
            "citing_opinion": item.get("citing_opinion"),
            "cited_opinion": item.get("cited_opinion"),
            "depth": item.get("depth"),
        })
    return {
        "total_cited_cases": result.get("count", 0),
        "citations": citations,
    }


@mcp.tool
def parse_legal_citations(text: str) -> dict:
    """Parse legal citations from text and identify the cases referenced.

    Handles Bluebook-format citations like "347 U.S. 483 (1954)" or "42 F.3d 1421".

    Args:
        text: Text containing legal citations to parse
    """
    parsed = parse_citation(text)
    return {
        "citations_found": len(parsed),
        "citations": [c.to_dict() for c in parsed],
    }


@mcp.tool
async def list_available_courts() -> dict:
    """List all available US courts and their short codes.

    Use this to find the correct court code for filtering searches.
    """
    result = await courtlistener.list_courts()
    courts = []
    for court in result.get("results", []):
        courts.append({
            "id": court.get("id"),
            "short_name": court.get("short_name"),
            "full_name": court.get("full_name"),
            "jurisdiction": court.get("jurisdiction"),
        })
    return {"courts": courts}


@mcp.tool
def list_reporter_abbreviations() -> dict:
    """List common legal reporter abbreviations and which courts they cover.

    Useful for understanding citations like '347 U.S. 483' or '42 F.3d 1421'.
    """
    return {"reporters": REPORTERS}


# --- Clio Practice Management Tools ---

@mcp.tool
async def search_clients(
    query: Optional[str] = None,
    contact_type: Optional[str] = None,
) -> dict:
    """Search for clients/contacts in Clio practice management.

    Requires Clio API token. Use this to look up client info, phone numbers, emails.

    Args:
        query: Search by name, email, or phone number
        contact_type: Filter by 'Person' or 'Company'
    """
    result = await clio.search_contacts(query=query, contact_type=contact_type)
    return {"contacts": result.get("data", []), "total": result.get("meta", {}).get("records", 0)}


@mcp.tool
async def search_matters(
    query: Optional[str] = None,
    status: Optional[str] = None,
    client_id: Optional[int] = None,
) -> dict:
    """Search for matters (cases) in Clio practice management.

    Requires Clio API token. Find open cases, filter by status or client.

    Args:
        query: Search by matter number or description
        status: Filter by 'Open', 'Closed', or 'Pending'
        client_id: Filter by client contact ID
    """
    result = await clio.search_matters(query=query, status=status, client_id=client_id)
    return {"matters": result.get("data", []), "total": result.get("meta", {}).get("records", 0)}


@mcp.tool
async def get_matter_details(matter_id: int) -> dict:
    """Get full details of a specific matter (case) from Clio.

    Includes client info, practice area, responsible attorney, billing method, deadlines.

    Args:
        matter_id: The Clio matter ID
    """
    result = await clio.get_matter(matter_id)
    return result.get("data", {})


@mcp.tool
async def get_time_entries(
    matter_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> dict:
    """Get time entries (billable hours) from Clio.

    Use this to review time spent on a case or by an attorney.

    Args:
        matter_id: Filter by matter/case ID
        date_from: Start date (YYYY-MM-DD)
        date_to: End date (YYYY-MM-DD)
    """
    result = await clio.get_time_entries(
        matter_id=matter_id, date_from=date_from, date_to=date_to
    )
    return {"entries": result.get("data", []), "total": result.get("meta", {}).get("records", 0)}


@mcp.tool
async def get_matter_tasks(
    matter_id: Optional[int] = None,
    status: Optional[str] = None,
) -> dict:
    """Get tasks associated with a matter in Clio.

    Args:
        matter_id: Filter by matter/case ID
        status: 'Complete' or 'Incomplete'
    """
    result = await clio.get_tasks(matter_id=matter_id, status=status)
    return {"tasks": result.get("data", []), "total": result.get("meta", {}).get("records", 0)}


@mcp.tool
async def get_matter_documents(
    matter_id: Optional[int] = None,
    query: Optional[str] = None,
) -> dict:
    """Search documents in Clio, optionally filtered by matter.

    Args:
        matter_id: Filter by matter/case ID
        query: Search by document name
    """
    result = await clio.get_documents(matter_id=matter_id, query=query)
    return {"documents": result.get("data", []), "total": result.get("meta", {}).get("records", 0)}


@mcp.tool
async def get_calendar(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    matter_id: Optional[int] = None,
) -> dict:
    """Get calendar entries (hearings, deadlines, meetings) from Clio.

    Args:
        date_from: Start date (YYYY-MM-DD)
        date_to: End date (YYYY-MM-DD)
        matter_id: Filter by matter/case ID
    """
    result = await clio.get_calendar_entries(
        date_from=date_from, date_to=date_to, matter_id=matter_id
    )
    return {"entries": result.get("data", []), "total": result.get("meta", {}).get("records", 0)}


# --- PACER Court Filings Tools ---

@mcp.tool
async def search_federal_cases(
    case_name: Optional[str] = None,
    case_number: Optional[str] = None,
    court_id: Optional[str] = None,
    date_filed_from: Optional[str] = None,
    date_filed_to: Optional[str] = None,
) -> dict:
    """Search PACER for federal court cases and filings.

    Requires PACER credentials. Use this to find active federal cases,
    check filing status, or look up case numbers.

    Args:
        case_name: Party name or case title (e.g., "Smith v. Jones")
        case_number: Specific case number (e.g., "1:23-cv-01234")
        court_id: Court code (e.g., 'nysd', 'cacd', 'txed')
        date_filed_from: Start date (MM/DD/YYYY)
        date_filed_to: End date (MM/DD/YYYY)
    """
    result = await pacer.search_cases(
        case_name=case_name,
        case_number=case_number,
        court_id=court_id,
        date_filed_from=date_filed_from,
        date_filed_to=date_filed_to,
    )
    return result


@mcp.tool
async def get_federal_case(case_id: str, court_id: str) -> dict:
    """Get details of a specific federal case from PACER.

    Args:
        case_id: The PACER case ID
        court_id: The court code (e.g., 'nysd')
    """
    return await pacer.get_case(case_id, court_id)


@mcp.tool
async def get_court_filings(
    case_id: str,
    court_id: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> dict:
    """Get docket entries (individual filings) for a federal case from PACER.

    Shows motions, orders, briefs, and other documents filed in the case.

    Args:
        case_id: The PACER case ID
        court_id: The court code (e.g., 'nysd')
        date_from: Start date filter (MM/DD/YYYY)
        date_to: End date filter (MM/DD/YYYY)
    """
    return await pacer.get_docket_entries(
        case_id=case_id,
        court_id=court_id,
        date_from=date_from,
        date_to=date_to,
    )


# --- Resources ---

@mcp.resource("legal://courts/federal")
def federal_courts_guide() -> str:
    """Guide to the US federal court system hierarchy."""
    return """
US Federal Court System:

1. Supreme Court of the United States (SCOTUS)
   - Code: scotus
   - Highest court, final authority on constitutional questions

2. Circuit Courts of Appeals (13 circuits)
   - Codes: ca1-ca11, cadc (D.C. Circuit), cafc (Federal Circuit)
   - Hear appeals from district courts within their circuit

3. District Courts (94 districts)
   - Codes vary: e.g., nysd (S.D.N.Y.), cacd (C.D. Cal.)
   - Trial courts for federal cases

4. Bankruptcy Courts
   - Handle bankruptcy filings under federal law

5. Specialized Courts
   - Court of International Trade, Court of Federal Claims, Tax Court
"""


@mcp.resource("legal://citation-guide")
def citation_guide() -> str:
    """Quick reference for reading legal citations."""
    return """
Legal Citation Quick Reference (Bluebook Format):

Format: Volume Reporter Page (Court Year)

Examples:
- 347 U.S. 483 (1954) = Volume 347, United States Reports, page 483, decided 1954
  (This is Brown v. Board of Education)

- 570 U.S. 529 (2013) = Volume 570, United States Reports, page 529, decided 2013
  (This is Shelby County v. Holder)

- 42 F.3d 1421 (D.C. Cir. 1994) = Volume 42, Federal Reporter 3rd Series,
  page 1421, D.C. Circuit Court, decided 1994

Common Reporters:
- U.S. = United States Reports (Supreme Court)
- S. Ct. = Supreme Court Reporter
- F.2d/F.3d/F.4th = Federal Reporter (Circuit Courts)
- F. Supp./F. Supp. 2d/3d = Federal Supplement (District Courts)
"""


def main():
    try:
        mcp.run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
