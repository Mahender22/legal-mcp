"""Tests for the PACER PCL Case Locator request shape.

These lock in the fix for issue #2: the search must POST to /cases/find with a
JSON body using PCL field names, not GET /cases with query params. They mock the
transport, so they verify the request we build without needing a live PACER
account.
"""

import pytest
from unittest.mock import AsyncMock, patch
from legal_mcp.src import pacer


@pytest.mark.asyncio
async def test_search_cases_posts_to_pcl_find_endpoint():
    with patch.object(pacer, "_request", new=AsyncMock(return_value={})) as mock_req:
        await pacer.search_cases(
            case_name="Brizuela v. Sparks",
            court_id="nvd",
            date_filed_from="2024-01-01",
            date_filed_to="2024-12-31",
            nature_of_suit="190",
        )

    method, url = mock_req.call_args.args
    body = mock_req.call_args.kwargs["json"]

    assert method == "post"
    assert url.endswith("/pcl-public-api/rest/cases/find")

    # PCL field names and array-typed criteria.
    assert body["caseTitle"] == "Brizuela v. Sparks"
    assert body["courtId"] == ["nvd"]
    assert body["natureOfSuit"] == ["190"]
    assert body["dateFiledFrom"] == "2024-01-01"
    assert body["dateFiledTo"] == "2024-12-31"

    # Legacy GET-style fields must be gone.
    assert "caseName" not in body
    assert "caseNumber" not in body
    assert "pageNumber" not in body


@pytest.mark.asyncio
async def test_search_cases_omits_empty_criteria():
    with patch.object(pacer, "_request", new=AsyncMock(return_value={})) as mock_req:
        await pacer.search_cases(case_name="Smith v. Jones")

    body = mock_req.call_args.kwargs["json"]
    assert body == {"caseTitle": "Smith v. Jones"}


@pytest.mark.asyncio
async def test_generate_otp_empty_without_secret():
    with patch.object(pacer, "PACER_TOTP_SECRET", ""):
        assert pacer._generate_otp() == ""
