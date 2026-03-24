# Changelog

All notable changes to LegalMCP will be documented in this file.

## [0.1.0] - 2026-03-24

### Added

- **18 MCP tools** across three legal integrations
- **CourtListener** (8 tools): case law search, case details, docket records, citation tracing (forward + backward), Bluebook citation parsing, court listing, reporter abbreviations
- **Clio** (7 tools): client search, matter management, time entries, tasks, documents, calendar
- **PACER** (3 tools): federal case search, case details, docket entry filings
- **2 MCP resources**: federal courts guide, citation format reference
- **Bluebook citation parser** with 30+ reporter abbreviations
- **Demo mode** — try all CourtListener tools without API keys (`LEGAL_MCP_DEMO=true`)
- **Error handling** — helpful messages for timeouts, auth failures, rate limits, and connection issues
- **Landing page** — dark "Chambers" theme with waitlist signup
- **Waitlist API** — FastAPI backend with SQLite storage
- **Docker support** — Dockerfile and docker-compose.yml
- **CI/CD** — GitHub Actions for tests (Python 3.10-3.12) and PyPI publishing
- **25 tests** — full mock coverage for all API clients and error paths
