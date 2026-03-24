# LegalMCP

The first comprehensive US legal MCP server for AI assistants.

Connect Claude, GPT, Cursor, or any MCP-compatible AI to:
- **4M+ US court opinions** via CourtListener
- **Citation parsing & tracing** (Bluebook format)
- **Clio practice management** (contacts, matters, billing, docs)
- **PACER federal court filings** (dockets, filings, case records)

## Quick Start

### Install

```bash
pip install legal-mcp
```

### Run

```bash
legal-mcp
```

### Connect to Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "legal-mcp": {
      "command": "legal-mcp"
    }
  }
}
```

### Connect to Claude Code

Add to your `.mcp.json`:

```json
{
  "mcpServers": {
    "legal-mcp": {
      "command": "legal-mcp"
    }
  }
}
```

## Configuration

Set environment variables for premium features:

```bash
# CourtListener (free account at courtlistener.com)
export COURTLISTENER_TOKEN="your-token"

# Clio (Pro plan — OAuth token from developer.clio.com)
export CLIO_TOKEN="your-oauth-token"

# PACER (Pro plan — account at pacer.uscourts.gov)
export PACER_USERNAME="your-username"
export PACER_PASSWORD="your-password"
```

## Tools Available

### Case Law (Starter + Pro)
| Tool | Description |
|------|-------------|
| `search_case_law` | Search millions of US court opinions by topic, court, date |
| `get_case_details` | Get full opinion text for a specific case |
| `get_case_record` | Get docket info — parties, judges, procedural history |
| `find_citing_cases` | Find cases that cite a specific opinion |
| `find_cited_cases` | Find cases that an opinion relies on |
| `parse_legal_citations` | Parse Bluebook citations from any text |
| `list_available_courts` | List all 400+ courts and their codes |
| `list_reporter_abbreviations` | Decode reporter abbreviations |

### Practice Management (Pro)
| Tool | Description |
|------|-------------|
| `search_clients` | Search Clio contacts by name, email, phone |
| `search_matters` | Search matters by number, description, status |
| `get_matter_details` | Full matter info — client, billing, deadlines |
| `get_time_entries` | Billable hours by matter, attorney, date range |
| `get_matter_tasks` | Tasks and to-dos for a matter |
| `get_matter_documents` | Documents attached to a matter |
| `get_calendar` | Hearings, deadlines, and meetings |

### Court Filings (Pro)
| Tool | Description |
|------|-------------|
| `search_federal_cases` | Search PACER for federal cases |
| `get_federal_case` | Get case details from PACER |
| `get_court_filings` | Get docket entries and filings |

## Pricing

- **Starter** ($79/mo): Case law search, citations, 400+ courts
- **Pro** ($149/mo): Everything in Starter + Clio + PACER + priority support

## License

MIT
