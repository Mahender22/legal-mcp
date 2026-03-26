# LegalMCP

[![CI](https://github.com/Mahender22/legal-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/Mahender22/legal-mcp/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/legal-mcp.svg)](https://pypi.org/project/legal-mcp/)

**The first comprehensive US legal MCP server for AI assistants.**

Connect Claude, GPT, Cursor, or any MCP-compatible AI to 4M+ US court opinions, Clio practice management, and PACER federal filings. Research in seconds, not hours.

---

## 30-Second Demo

```
You:  Find Supreme Court cases about Fourth Amendment and cell phone location data

LegalMCP:  Found 52 results. Top case:

  Carpenter v. United States, 585 U.S. 296 (2018)
  The Court held that accessing historical cell-site location
  information constitutes a search under the Fourth Amendment,
  requiring a warrant supported by probable cause.

  → 127 cases cite this opinion
  → Full text: courtlistener.com/opinion/4578834
```

## Why LegalMCP?

| | Traditional Research | AI + LegalMCP |
|---|---|---|
| Find relevant cases | 45-90 min | **< 30 sec** |
| Trace citation history | Open Westlaw, click around | *"Who cited this case?"* |
| Pull client billing | Log into Clio, navigate menus | *"Total hours on Henderson?"* |
| Monthly cost | $200-400 (Westlaw/Lexis) | **$79/mo** |

## Quick Start

### Install

We recommend using a virtual environment to avoid conflicts with other packages:

```bash
# Create and activate a virtual environment
python -m venv legal-mcp-env

# Windows
legal-mcp-env\Scripts\activate

# Mac/Linux
source legal-mcp-env/bin/activate

# Install
pip install legal-mcp
```

Or install from GitHub:
```bash
pip install git+https://github.com/Mahender22/legal-mcp.git
```

### Run

Want to try it without API keys? Enable demo mode first (optional):

```bash
# Mac/Linux
export LEGAL_MCP_DEMO=true

# Windows
set LEGAL_MCP_DEMO=true
```

Then start the server:

```bash
legal-mcp
```

### Connect to Claude Desktop

Add to your `claude_desktop_config.json`:

**Windows** (`%APPDATA%\Claude\claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "legal-mcp": {
      "command": "C:/path/to/legal-mcp-env/Scripts/legal-mcp.exe",
      "env": {
        "LEGAL_MCP_DEMO": "true"
      }
    }
  }
}
```

**Mac/Linux** (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "legal-mcp": {
      "command": "/path/to/legal-mcp-env/bin/legal-mcp",
      "env": {
        "LEGAL_MCP_DEMO": "true"
      }
    }
  }
}
```

> **Note:** Use the full path to `legal-mcp` inside your virtual environment. Remove the `LEGAL_MCP_DEMO` line and add your API keys for real data (see [SETUP.md](SETUP.md)).

### Connect to Claude Code

Run this command to add LegalMCP globally (available in every session):

**Mac/Linux:**
```bash
claude mcp add legal-mcp /path/to/legal-mcp-env/bin/legal-mcp
```

**Windows:**
```bash
claude mcp add legal-mcp C:\path\to\legal-mcp-env\Scripts\legal-mcp.exe
```

To enable demo mode, add the env flag:

**Mac/Linux:**
```bash
claude mcp add legal-mcp -e LEGAL_MCP_DEMO=true -- /path/to/legal-mcp-env/bin/legal-mcp
```

**Windows:**
```bash
claude mcp add legal-mcp -e LEGAL_MCP_DEMO=true -- C:\path\to\legal-mcp-env\Scripts\legal-mcp.exe
```

> **Tip:** To add it to a specific project only, add `-s project` flag or create a `.mcp.json` file in your project root.

### Connect to Cursor / Windsurf

LegalMCP works with any MCP-compatible client. Add the `legal-mcp` command to your AI tool's MCP server configuration.

## Configuration

Set environment variables for API access. See [SETUP.md](SETUP.md) for step-by-step instructions.

| Variable | Required | Plan | Description |
|----------|----------|------|-------------|
| `COURTLISTENER_TOKEN` | Optional | Free | Higher rate limits for case law search |
| `CLIO_TOKEN` | For Clio tools | Pro | OAuth token for practice management |
| `PACER_USERNAME` | For PACER tools | Pro | PACER account username |
| `PACER_PASSWORD` | For PACER tools | Pro | PACER account password |
| `LEGAL_MCP_DEMO` | Optional | — | Set `true` for demo mode (no API keys) |

## All 18 Tools

### Case Law (Starter + Pro)

| Tool | What It Does |
|------|-------------|
| `search_case_law` | Search 4M+ US court opinions by topic, court, date range |
| `get_case_details` | Get full opinion text for a specific case |
| `get_case_record` | Get docket — parties, judges, procedural history |
| `find_citing_cases` | Find cases that cite a specific opinion |
| `find_cited_cases` | Find cases that an opinion relies on |
| `parse_legal_citations` | Parse Bluebook citations from any text |
| `list_available_courts` | List all 400+ courts and their codes |
| `list_reporter_abbreviations` | Decode reporter abbreviations (U.S., F.3d, etc.) |

### Practice Management — Clio (Pro)

| Tool | What It Does |
|------|-------------|
| `search_clients` | Search contacts by name, email, phone |
| `search_matters` | Search matters by number, description, status |
| `get_matter_details` | Full matter info — client, billing, deadlines |
| `get_time_entries` | Billable hours by matter, attorney, date range |
| `get_matter_tasks` | Tasks and to-dos for a matter |
| `get_matter_documents` | Documents attached to a matter |
| `get_calendar` | Hearings, deadlines, and meetings |

### Court Filings — PACER (Pro)

| Tool | What It Does |
|------|-------------|
| `search_federal_cases` | Search PACER for federal court cases |
| `get_federal_case` | Get case details from PACER |
| `get_court_filings` | Get docket entries and filings |

## Docker

```bash
# Copy and configure environment
cp .env.example .env
# Edit .env with your API keys

# Run
docker-compose up
```

This starts the MCP server on port 8000 and the waitlist API on port 8080.

## How It Works

LegalMCP is a [Model Context Protocol](https://modelcontextprotocol.io/) server. MCP is an open standard that lets AI assistants call external tools — like searching case law or querying your Clio data.

```
┌──────────────┐     MCP      ┌──────────────┐      API      ┌──────────────┐
│              │  ──────────►  │              │  ──────────►  │              │
│  Claude /    │   Tool calls  │   LegalMCP   │   HTTP        │ CourtListener│
│  GPT /       │  ◄──────────  │   Server     │  ◄──────────  │ Clio / PACER │
│  Cursor      │   Results     │  (your PC)   │   JSON        │              │
└──────────────┘               └──────────────┘               └──────────────┘
```

Your data stays on your machine. LegalMCP runs locally and connects directly to the APIs.

## Pricing

| | Starter | Pro |
|---|---|---|
| **Price** | $79/mo | $149/mo |
| Case law search (4M+ opinions) | Yes | Yes |
| Citation parsing & tracing | Yes | Yes |
| 400+ courts & jurisdictions | Yes | Yes |
| Clio integration | — | Yes |
| PACER access | — | Yes |
| Priority support | — | Yes |

*Less than one billable hour. Pays for itself the first time it saves you a 3-hour research session.*

## Development

```bash
# Clone and install
git clone https://github.com/Mahender22/legal-mcp.git
cd legal-mcp
pip install -e ".[dev,waitlist]"

# Run tests
pytest legal_mcp/tests/ -v

# Run server locally
python -m legal_mcp.src.server
```

## License

[MIT](LICENSE) — use it however you want.
