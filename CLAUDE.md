# LegalMCP — US Legal MCP Server

## Overview
The first comprehensive US legal MCP server connecting AI assistants to case law, practice management, and court filings. 18 tools + 2 resources via FastMCP.

## Architecture
- **Framework**: FastMCP 3.1.1 (Python)
- **APIs**: CourtListener (case law), Clio (practice management), PACER (court filings)
- **Pricing**: $79/mo starter, $149/mo pro
- **Deployment**: pip-installable, Docker, runs locally or hosted

## Structure
```
legal-mcp/
├── legal_mcp/
│   ├── src/
│   │   ├── server.py          # Main MCP server — all tools registered here
│   │   ├── courtlistener.py   # CourtListener API client (with error handling)
│   │   ├── clio.py            # Clio practice management client
│   │   ├── pacer.py           # PACER federal filings client
│   │   ├── citation_parser.py # Bluebook citation parser
│   │   ├── demo_data.py       # Pre-cached demo results (10 landmark cases)
│   │   └── config.py          # API URLs, env vars, DEMO_MODE
│   └── tests/                 # 33 tests
├── landing/
│   ├── index.html             # Landing page (dark "Chambers" theme)
│   └── api/
│       └── waitlist.py        # FastAPI waitlist backend
├── docs/
│   └── tools.md               # Comprehensive tool documentation
├── .github/workflows/
│   ├── ci.yml                 # Test pipeline (Python 3.10-3.12)
│   └── publish.yml            # PyPI publish on GitHub release
├── Dockerfile                 # Container deployment
├── docker-compose.yml         # Full stack (MCP + waitlist)
├── pyproject.toml             # Package config
├── SETUP.md                   # Credential acquisition guide
├── CHANGELOG.md               # Release notes
├── README.md                  # Marketing-grade README
└── LICENSE                    # MIT
```

## Commands
- `pip install -e ".[dev,waitlist]"` — install in dev mode
- `pytest legal_mcp/tests/ -v` — run all 33 tests
- `python -m legal_mcp.src.server` — run MCP server
- `LEGAL_MCP_DEMO=true python -m legal_mcp.src.server` — run in demo mode
- `python landing/api/waitlist.py` — run waitlist API on port 8080
- `docker-compose up` — run full stack via Docker

## Environment Variables
- `COURTLISTENER_TOKEN` — free from courtlistener.com (higher rate limits)
- `CLIO_TOKEN` — OAuth token from developer.clio.com (Pro plan)
- `PACER_USERNAME` / `PACER_PASSWORD` — from pacer.uscourts.gov (Pro plan)
- `LEGAL_MCP_DEMO` — set `true` for demo mode (no API keys needed)

## Status
- CourtListener: **LIVE** (tested with real API, 13 tests)
- Citation Parser: **LIVE** (5 tests passing)
- Demo Mode: **LIVE** (8 tests passing, 10 landmark cases)
- Error Handling: **LIVE** (7 tests — timeouts, auth, rate limits)
- Clio: **BUILT** (needs API token to test live)
- PACER: **BUILT** (needs PACER account to test live)
- Landing Page: **LIVE** (SEO, plan selector, social proof, GitHub link)
- Waitlist API: **LIVE** (5 tests passing)
- CI/CD: **LIVE** (GitHub Actions for tests + PyPI publish)
- Docker: **LIVE** (Dockerfile + docker-compose)
- Documentation: **LIVE** (README, SETUP.md, CHANGELOG, docs/tools.md)
