# LegalMCP Marketing-Ready Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Take LegalMCP from working MVP to marketing-ready product across two phases — Phase 1 makes it launchable, Phase 2 adds professional polish.

**Architecture:** The server core is solid (18 tools, 18 tests). We're adding infrastructure (CI, Docker, env), resilience (error handling, demo mode), and marketing surface (README, docs, landing page improvements). No architectural changes to the server itself.

**Tech Stack:** Python 3.10+, FastMCP, httpx, pytest, GitHub Actions, Docker, Hatch/PyPI

---

## Phase 1 — Marketing Launch

### Task 1: .env.example and project hygiene

**Files:**
- Create: `.env.example`
- Modify: `.gitignore`

- [ ] **Step 1: Create .env.example**

```bash
# LegalMCP Environment Variables
# Copy to .env and fill in your values

# CourtListener — FREE (get token at https://www.courtlistener.com/sign-in/)
# Optional: works without token but with lower rate limits
COURTLISTENER_TOKEN=

# Clio Practice Management — PRO plan only
# Get OAuth token at https://developer.clio.com
CLIO_TOKEN=

# PACER Federal Court Filings — PRO plan only
# Register at https://pacer.uscourts.gov
PACER_USERNAME=
PACER_PASSWORD=
```

- [ ] **Step 2: Add .env.example protection to .gitignore**

Append to existing `.gitignore`:
```
# Secrets
.env.local
waitlist.db

# OS
.DS_Store
Thumbs.db
```

- [ ] **Step 3: Commit**

```bash
git add .env.example .gitignore
git commit -m "chore: add .env.example and expand .gitignore"
```

---

### Task 2: Error handling and resilience in API clients

**Files:**
- Modify: `legal_mcp/src/courtlistener.py`
- Modify: `legal_mcp/src/clio.py`
- Modify: `legal_mcp/src/pacer.py`
- Create: `legal_mcp/tests/test_error_handling.py`

- [ ] **Step 1: Write failing tests for error handling**

```python
# legal_mcp/tests/test_error_handling.py
"""Tests for API client error handling."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx


@pytest.mark.asyncio
async def test_courtlistener_timeout_returns_helpful_error():
    mock_client = MagicMock()
    mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("Connection timed out"))
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("httpx.AsyncClient", return_value=mock_client):
        from legal_mcp.src import courtlistener
        with pytest.raises(ConnectionError, match="CourtListener"):
            await courtlistener.search_opinions(query="test")


@pytest.mark.asyncio
async def test_courtlistener_401_returns_auth_error():
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.raise_for_status = MagicMock(
        side_effect=httpx.HTTPStatusError("401", request=MagicMock(), response=mock_response)
    )
    mock_client = MagicMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("httpx.AsyncClient", return_value=mock_client):
        from legal_mcp.src import courtlistener
        with pytest.raises(PermissionError, match="COURTLISTENER_TOKEN"):
            await courtlistener.search_opinions(query="test")


@pytest.mark.asyncio
async def test_clio_missing_token_error():
    from legal_mcp.src import clio
    with patch.object(clio, "CLIO_TOKEN", ""):
        with pytest.raises(ValueError, match="CLIO_TOKEN"):
            await clio.search_contacts(query="test")


@pytest.mark.asyncio
async def test_pacer_missing_credentials_error():
    from legal_mcp.src import pacer
    pacer._token_cache["token"] = None
    with patch.object(pacer, "PACER_USERNAME", ""), patch.object(pacer, "PACER_PASSWORD", ""):
        with pytest.raises(ValueError, match="PACER"):
            await pacer.search_cases(case_name="test")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest legal_mcp/tests/test_error_handling.py -v`
Expected: FAIL — error types don't match yet

- [ ] **Step 3: Add error handling wrapper to courtlistener.py**

Add at the top of `courtlistener.py` after imports:

```python
async def _request(method: str, url: str, **kwargs) -> dict:
    """Make HTTP request with proper error handling."""
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
```

Then refactor each function to use `_request()` instead of raw httpx calls.

- [ ] **Step 4: Add token validation to clio.py**

Add at the top of `_get()`:
```python
if not CLIO_TOKEN:
    raise ValueError(
        "Clio API token not set. Set the CLIO_TOKEN environment variable. "
        "Get an OAuth token at https://developer.clio.com (requires Pro plan)."
    )
```

Add similar try/except wrapping as courtlistener.

- [ ] **Step 5: PACER already validates credentials — add timeout/HTTP error handling**

Wrap `_authenticate()` and each request function with try/except for timeout and HTTP errors, similar to courtlistener pattern.

- [ ] **Step 6: Run all tests**

Run: `pytest legal_mcp/tests/ -v`
Expected: All 22 tests pass (18 existing + 4 new)

- [ ] **Step 7: Commit**

```bash
git add legal_mcp/src/courtlistener.py legal_mcp/src/clio.py legal_mcp/src/pacer.py legal_mcp/tests/test_error_handling.py
git commit -m "feat: add helpful error messages for API failures"
```

---

### Task 3: GitHub Actions CI pipeline

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: Create CI workflow**

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev,waitlist]"

      - name: Run tests
        run: pytest legal_mcp/tests/ -v --tb=short

      - name: Check import works
        run: python -c "from legal_mcp.src.server import mcp; print(f'Server: {mcp.name}')"
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: add GitHub Actions test pipeline for Python 3.10-3.12"
```

---

### Task 4: Dockerfile and docker-compose

**Files:**
- Create: `Dockerfile`
- Create: `docker-compose.yml`

- [ ] **Step 1: Create Dockerfile**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY legal_mcp/ legal_mcp/

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["legal-mcp"]
```

- [ ] **Step 2: Create docker-compose.yml**

```yaml
version: "3.8"

services:
  legal-mcp:
    build: .
    env_file: .env
    ports:
      - "8000:8000"
    restart: unless-stopped

  waitlist:
    build: .
    command: python landing/api/waitlist.py
    ports:
      - "8080:8080"
    volumes:
      - waitlist-data:/app/landing/api
    restart: unless-stopped

volumes:
  waitlist-data:
```

- [ ] **Step 3: Add Docker to .gitignore**

Append to `.gitignore`:
```
# Docker
*.db
```

- [ ] **Step 4: Test Docker build locally**

Run: `docker build -t legal-mcp .`
Expected: Build succeeds

- [ ] **Step 5: Commit**

```bash
git add Dockerfile docker-compose.yml .gitignore
git commit -m "feat: add Dockerfile and docker-compose for easy deployment"
```

---

### Task 5: SETUP.md — Credential acquisition guide

**Files:**
- Create: `SETUP.md`

- [ ] **Step 1: Write SETUP.md**

Comprehensive guide covering:
1. **CourtListener (free)** — Step-by-step: go to courtlistener.com, create account, get API token from profile page
2. **Clio (Pro plan)** — Step-by-step: register at developer.clio.com, create OAuth app, get token
3. **PACER (Pro plan)** — Step-by-step: register at pacer.uscourts.gov, note $0.10/page fee structure
4. **Verifying setup** — How to test each integration works
5. **Troubleshooting** — Common errors and fixes

- [ ] **Step 2: Commit**

```bash
git add SETUP.md
git commit -m "docs: add step-by-step credential setup guide"
```

---

### Task 6: Marketing-grade README

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Rewrite README.md**

Structure:
```markdown
# LegalMCP

[![CI](badge-url)](actions-url) [![Python 3.10+](badge)](url) [![License: MIT](badge)](url) [![PyPI](badge)](url)

**The first comprehensive US legal MCP server for AI assistants.**

> Connect Claude, GPT, or any MCP client to 4M+ US court opinions, Clio practice management, and PACER federal filings.

## 30-Second Demo

[Code block showing: install → run → use in Claude Desktop with a real Fourth Amendment query and result]

## Why LegalMCP?

| | Traditional Research | AI + LegalMCP |
|---|---|---|
| Find relevant cases | 45-90 min | < 30 sec |
| Check citation history | Open new tool, search | "Who cited this case?" |
| Pull client billing | Log into Clio, navigate | "Total billable hours on Henderson?" |
| Monthly cost | $200-400 (Westlaw) | $79/mo |

## Quick Start

### Install
pip install legal-mcp

### Run
legal-mcp

### Connect to Claude Desktop / Claude Code / Cursor
[Config snippets for each]

## Configuration
[Env vars table with links to SETUP.md]

## All 18 Tools
[Three tables: Case Law, Practice Management, Court Filings with descriptions]

## Docker
docker-compose up

## How It Works
[Brief MCP explanation with diagram-in-text]

## Pricing
[Starter $79 vs Pro $149 with feature comparison]

## Contributing / License / Links
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: rewrite README for marketing — badges, demo, comparison table"
```

---

### Task 7: CHANGELOG.md

**Files:**
- Create: `CHANGELOG.md`

- [ ] **Step 1: Write CHANGELOG**

```markdown
# Changelog

## [0.1.0] - 2026-03-24

### Added
- 18 MCP tools across three integrations
- **CourtListener** (8 tools): case law search, case details, citation tracing, citation parsing, court listing
- **Clio** (7 tools): client search, matter management, time entries, tasks, documents, calendar
- **PACER** (3 tools): federal case search, case details, court filings
- 2 MCP resources: federal courts guide, citation format guide
- Bluebook citation parser with 30+ reporter abbreviations
- Landing page with waitlist signup
- FastAPI waitlist backend with SQLite
- 18+ tests with full mock coverage
- Docker support
- GitHub Actions CI
```

- [ ] **Step 2: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs: add CHANGELOG for v0.1.0"
```

---

### Task 8: Landing page improvements

**Files:**
- Modify: `landing/index.html`

- [ ] **Step 1: Add GitHub link to nav**

In the nav section, add a GitHub icon link before the "Join Waitlist" CTA.

- [ ] **Step 2: Add plan selector to waitlist form**

Replace the hardcoded `plan: 'starter'` with a toggle/radio button so users can select Starter or Pro interest.

- [ ] **Step 3: Add social proof section after stats**

Add a "Trusted by" or "Built on" section showing:
- CourtListener logo/name (data source credibility)
- "Open source" badge
- "MCP Protocol" badge
- GitHub stars badge (dynamic)

- [ ] **Step 4: Add meta tags for SEO and social sharing**

```html
<meta property="og:title" content="LegalMCP — US Case Law for AI Assistants">
<meta property="og:description" content="Connect Claude or GPT to 4M+ US court opinions, Clio, and PACER.">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
```

- [ ] **Step 5: Test landing page loads correctly**

Open `landing/index.html` in a browser and verify all sections render.

- [ ] **Step 6: Commit**

```bash
git add landing/index.html
git commit -m "feat: landing page — GitHub link, plan selector, social proof, SEO meta tags"
```

---

## Phase 2 — Professional Polish

### Task 9: Demo/sandbox mode with cached CourtListener responses

**Files:**
- Create: `legal_mcp/src/demo_data.py`
- Modify: `legal_mcp/src/config.py`
- Modify: `legal_mcp/src/courtlistener.py`
- Create: `legal_mcp/tests/test_demo_mode.py`

- [ ] **Step 1: Write failing tests for demo mode**

```python
# legal_mcp/tests/test_demo_mode.py
"""Tests for demo/sandbox mode."""
import pytest
from unittest.mock import patch


@pytest.mark.asyncio
async def test_demo_mode_returns_cached_search():
    with patch("legal_mcp.src.config.DEMO_MODE", True):
        from legal_mcp.src import courtlistener
        result = await courtlistener.search_opinions(query="fourth amendment")
        assert result["count"] > 0
        assert len(result["results"]) > 0
        assert "Carpenter" in str(result) or "fourth" in str(result).lower()


@pytest.mark.asyncio
async def test_demo_mode_search_any_query_returns_results():
    with patch("legal_mcp.src.config.DEMO_MODE", True):
        from legal_mcp.src import courtlistener
        result = await courtlistener.search_opinions(query="breach of contract")
        assert result["count"] > 0


def test_demo_mode_defaults_to_false():
    from legal_mcp.src.config import DEMO_MODE
    # DEMO_MODE should be False unless explicitly set
    assert DEMO_MODE is False or DEMO_MODE == False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest legal_mcp/tests/test_demo_mode.py -v`
Expected: FAIL

- [ ] **Step 3: Add DEMO_MODE to config.py**

```python
DEMO_MODE = os.environ.get("LEGAL_MCP_DEMO", "").lower() in ("1", "true", "yes")
```

- [ ] **Step 4: Create demo_data.py with curated case law responses**

Pre-cache ~10 famous cases spanning different legal areas:
- Constitutional law: Carpenter v. US, Brown v. Board, Miranda v. Arizona
- Contract law: Hadley v. Baxendale pattern
- Tort law: Palsgraf v. Long Island Railroad
- IP: Alice Corp v. CLS Bank

Each entry should mirror the exact CourtListener API response format.

- [ ] **Step 5: Wire demo mode into courtlistener.py**

At the top of `search_opinions()`, add:
```python
from .config import DEMO_MODE
if DEMO_MODE:
    from .demo_data import get_demo_results
    return get_demo_results(query)
```

Similarly for `get_opinion()`, `get_docket()`, and citation functions.

- [ ] **Step 6: Run all tests**

Run: `pytest legal_mcp/tests/ -v`
Expected: All tests pass (existing + new demo tests)

- [ ] **Step 7: Update .env.example**

Add:
```bash
# Demo mode — try LegalMCP without any API keys
# Set to "true" to use pre-cached sample data
LEGAL_MCP_DEMO=false
```

- [ ] **Step 8: Commit**

```bash
git add legal_mcp/src/demo_data.py legal_mcp/src/config.py legal_mcp/src/courtlistener.py legal_mcp/tests/test_demo_mode.py .env.example
git commit -m "feat: add demo mode — try LegalMCP without API keys"
```

---

### Task 10: PyPI publishing workflow

**Files:**
- Create: `.github/workflows/publish.yml`
- Modify: `pyproject.toml`

- [ ] **Step 1: Add project URLs to pyproject.toml**

```toml
[project.urls]
Homepage = "https://github.com/Mahender22/legal-mcp"
Documentation = "https://github.com/Mahender22/legal-mcp#readme"
Repository = "https://github.com/Mahender22/legal-mcp"
Issues = "https://github.com/Mahender22/legal-mcp/issues"
Changelog = "https://github.com/Mahender22/legal-mcp/blob/main/CHANGELOG.md"
```

- [ ] **Step 2: Create publish workflow**

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    environment: pypi
    permissions:
      id-token: write

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install build tools
        run: pip install build

      - name: Build package
        run: python -m build

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
```

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/publish.yml pyproject.toml
git commit -m "ci: add PyPI publish workflow on GitHub release"
```

---

### Task 11: Comprehensive tool documentation

**Files:**
- Create: `docs/tools.md`

- [ ] **Step 1: Write tool documentation**

For each of the 18 tools, document:
- Name and description
- Parameters with types and examples
- Return value structure
- Example query and response
- Which plan it requires (Starter/Pro)

Group by integration: CourtListener, Clio, PACER.

Include the 2 MCP resources too.

- [ ] **Step 2: Link from README**

Add a "Full Documentation" link in README pointing to `docs/tools.md`.

- [ ] **Step 3: Commit**

```bash
git add docs/tools.md README.md
git commit -m "docs: add comprehensive tool documentation with examples"
```

---

### Task 12: Landing page final polish

**Files:**
- Modify: `landing/index.html`

- [ ] **Step 1: Add GitHub repo link in footer**

- [ ] **Step 2: Add "pip install legal-mcp" copy-to-clipboard in hero**

Add a small code snippet with a copy button below the main CTA.

- [ ] **Step 3: Add "Try Demo Mode" section**

Between pricing and FAQ, add a section explaining demo mode:
> "Want to try it first? Run with `LEGAL_MCP_DEMO=true legal-mcp` — no API keys needed."

- [ ] **Step 4: Improve mobile responsiveness**

Test and fix any layout issues on mobile viewport widths.

- [ ] **Step 5: Commit**

```bash
git add landing/index.html
git commit -m "feat: landing page — install snippet, demo mode section, mobile fixes"
```

---

### Task 13: Final verification and v0.1.0 tag

**Files:**
- Modify: `CLAUDE.md` (update status)

- [ ] **Step 1: Run full test suite**

Run: `pytest legal_mcp/tests/ -v`
Expected: All tests pass

- [ ] **Step 2: Verify package builds**

Run: `pip install -e . && legal-mcp --help` or `python -c "from legal_mcp.src.server import mcp; print(mcp.name)"`

- [ ] **Step 3: Verify Docker builds**

Run: `docker build -t legal-mcp .`

- [ ] **Step 4: Update CLAUDE.md status section**

Update all statuses to reflect current state.

- [ ] **Step 5: Final commit and tag**

```bash
git add -A
git commit -m "chore: v0.1.0 marketing-ready release"
git tag -a v0.1.0 -m "LegalMCP v0.1.0 — marketing-ready release"
```
