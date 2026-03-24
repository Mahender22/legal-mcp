# LegalMCP — US Legal MCP Server

## Overview
The first comprehensive US legal MCP server connecting AI assistants to case law, practice management, and court filings. 18 tools + 2 resources via FastMCP.

## Architecture
- **Framework**: FastMCP 3.1.1 (Python)
- **APIs**: CourtListener (case law), Clio (practice management), PACER (court filings)
- **Pricing**: $79/mo starter, $149/mo pro
- **Deployment**: pip-installable, runs locally or hosted

## Structure
```
legal-mcp/
├── legal_mcp/
│   ├── src/
│   │   ├── server.py          # Main MCP server — all tools registered here
│   │   ├── courtlistener.py   # CourtListener API client
│   │   ├── clio.py            # Clio practice management client
│   │   ├── pacer.py           # PACER federal filings client
│   │   ├── citation_parser.py # Bluebook citation parser
│   │   └── config.py          # API URLs and env var config
│   └── tests/                 # 18 tests
├── landing/
│   ├── index.html             # Landing page (dark "Chambers" theme)
│   └── api/
│       └── waitlist.py        # FastAPI waitlist backend
├── pyproject.toml             # Package config
└── README.md                  # Installation guide
```

## Commands
- `pip install -e .` — install in dev mode
- `pytest legal_mcp/tests/` — run tests
- `python -m legal_mcp.src.server` — run MCP server
- `python landing/api/waitlist.py` — run waitlist API on port 8080

## Environment Variables
- `COURTLISTENER_TOKEN` — free from courtlistener.com (higher rate limits)
- `CLIO_TOKEN` — OAuth token from developer.clio.com (Pro plan)
- `PACER_USERNAME` / `PACER_PASSWORD` — from pacer.uscourts.gov (Pro plan)

## Status
- CourtListener: **LIVE** (tested with real API)
- Citation Parser: **LIVE** (5 tests passing)
- Clio: **BUILT** (needs API token to test live)
- PACER: **BUILT** (needs PACER account to test live)
- Landing Page: **BUILT**
- Waitlist API: **BUILT** (5 tests passing)
