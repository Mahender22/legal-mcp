"""PACER API client for federal court filings."""

import httpx
from typing import Optional
from .config import PACER_USERNAME, PACER_PASSWORD, PACER_TOTP_SECRET

PACER_LOGIN_URL = "https://pacer.login.uscourts.gov/services/cso-auth"
PACER_SEARCH_URL = "https://pcl.uscourts.gov/pcl-public-api/rest"

_token_cache: dict = {"token": None}


def _generate_otp() -> str:
    """Return a TOTP code from PACER_TOTP_SECRET for MFA-enrolled accounts.

    Returns an empty string when no secret is configured, so accounts without
    MFA are unaffected. The `cryptography` dependency is imported lazily and is
    only required when PACER_TOTP_SECRET is set.
    """
    if not PACER_TOTP_SECRET:
        return ""
    import base64
    import time
    from cryptography.hazmat.primitives.twofactor.totp import TOTP
    from cryptography.hazmat.primitives.hashes import SHA1

    key = base64.b32decode(PACER_TOTP_SECRET)
    totp = TOTP(key=key, length=6, algorithm=SHA1(), time_step=30)
    return totp.generate(int(time.time())).decode()


async def _authenticate() -> str:
    """Authenticate with PACER and get a session token."""
    if _token_cache["token"]:
        return _token_cache["token"]

    if not PACER_USERNAME or not PACER_PASSWORD:
        raise ValueError(
            "PACER credentials not set. Set PACER_USERNAME and PACER_PASSWORD "
            "environment variables. Register at https://pacer.uscourts.gov "
            "(Note: PACER charges $0.10/page for document access)"
        )

    login_payload = {
        "loginId": PACER_USERNAME,
        "password": PACER_PASSWORD,
        # Filer / upgraded PACER accounts return no token without redactFlag.
        "redactFlag": "1",
    }
    # MFA-enrolled accounts also require a one-time code. Opt-in via
    # PACER_TOTP_SECRET; this stays a no-op for accounts without MFA.
    otp_code = _generate_otp()
    if otp_code:
        login_payload["otpCode"] = otp_code

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                PACER_LOGIN_URL,
                json=login_payload,
                headers={"Content-Type": "application/json", "Accept": "application/json"},
            )
            resp.raise_for_status()
            data = resp.json()
            token = data.get("nextGenCSO", data.get("loginResult", ""))
            _token_cache["token"] = token
            return token
    except httpx.TimeoutException:
        raise ConnectionError(
            "PACER authentication timed out. The service may be temporarily unavailable."
        )
    except httpx.HTTPStatusError as e:
        status = e.response.status_code
        if status == 401:
            raise PermissionError(
                "PACER login failed. Check your PACER_USERNAME and PACER_PASSWORD. "
                "Register at https://pacer.uscourts.gov"
            )
        raise ConnectionError(f"PACER authentication error (HTTP {status}): {e}")
    except httpx.ConnectError:
        raise ConnectionError("Cannot connect to PACER. Check your internet connection.")


async def _get_headers() -> dict:
    token = await _authenticate()
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-NEXT-GEN-CSO": token,
    }


async def _request(method: str, url: str, **kwargs) -> dict:
    """Make HTTP request to PACER with error handling."""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await getattr(client, method)(url, headers=await _get_headers(), **kwargs)
            resp.raise_for_status()
            # PACER may issue a refreshed session token in the response header.
            refreshed = resp.headers.get("X-NEXT-GEN-CSO")
            if refreshed:
                _token_cache["token"] = refreshed
            return resp.json()
    except httpx.TimeoutException:
        raise ConnectionError(
            "PACER API timed out. The service may be temporarily unavailable."
        )
    except httpx.HTTPStatusError as e:
        status = e.response.status_code
        if status == 401:
            _token_cache["token"] = None  # Clear stale token
            raise PermissionError(
                "PACER session expired. Try the request again to re-authenticate."
            )
        elif status == 429:
            raise ConnectionError("PACER rate limit exceeded. Wait a moment and try again.")
        raise ConnectionError(f"PACER API error (HTTP {status}): {e}")
    except httpx.ConnectError:
        raise ConnectionError("Cannot connect to PACER. Check your internet connection.")


async def search_cases(
    case_name: Optional[str] = None,
    case_number: Optional[str] = None,
    court_id: Optional[str] = None,
    date_filed_from: Optional[str] = None,
    date_filed_to: Optional[str] = None,
    nature_of_suit: Optional[str] = None,
    page: int = 0,
) -> dict:
    """Search PACER for federal court cases via the PCL Case Locator API.

    Sends POST /cases/find with a JSON body per the PACER Case Locator (PCL)
    API User Guide. Dates use YYYY-MM-DD; courtId and natureOfSuit are arrays.
    """
    search_body: dict = {}
    if case_name:
        search_body["caseTitle"] = case_name
    if case_number:
        search_body["caseNumberFull"] = case_number
    if court_id:
        search_body["courtId"] = [court_id]
    if date_filed_from:
        search_body["dateFiledFrom"] = date_filed_from
    if date_filed_to:
        search_body["dateFiledTo"] = date_filed_to
    if nature_of_suit:
        search_body["natureOfSuit"] = [nature_of_suit]

    params = {"page": page} if page else {}
    return await _request("post", f"{PACER_SEARCH_URL}/cases/find", json=search_body, params=params)


async def get_case(case_id: str, court_id: str) -> dict:
    """Get details of a specific PACER case."""
    return await _request("get", f"{PACER_SEARCH_URL}/cases/{case_id}", params={"courtId": court_id})


async def get_docket_entries(
    case_id: str,
    court_id: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    page: int = 1,
) -> dict:
    """Get docket entries (filings) for a PACER case."""
    params = {"courtId": court_id, "pageNumber": page}
    if date_from:
        params["dateFrom"] = date_from
    if date_to:
        params["dateTo"] = date_to

    return await _request("get", f"{PACER_SEARCH_URL}/cases/{case_id}/docket-entries", params=params)
