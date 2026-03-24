# LegalMCP Tool Documentation

Complete reference for all 18 tools and 2 resources provided by LegalMCP.

---

## Case Law Tools (Starter + Pro)

### search_case_law

Search millions of US court opinions by topic, court, and date range.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `query` | string | Yes | Legal search terms (e.g., "duty to mitigate breach of contract") |
| `court` | string | No | Court filter: `scotus`, `ca9`, `nysd`, etc. |
| `date_after` | string | No | Only cases after this date (YYYY-MM-DD) |
| `date_before` | string | No | Only cases before this date (YYYY-MM-DD) |

**Example:**
```
"Find Supreme Court cases about qualified immunity after 2020"
```

**Returns:** Up to 10 cases with case name, court, date, citation, snippet, and CourtListener URL.

---

### get_case_details

Get the full text and metadata of a specific court opinion.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `opinion_id` | integer | Yes | Opinion ID from a search result |

**Example:**
```
"Get the full text of opinion 2812209"
```

**Returns:** Opinion type, HTML text with citations (first 5000 chars), plain text, download URL, author, and joining judges.

---

### get_case_record

Get the complete docket (case record) including parties, attorneys, and procedural history.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `docket_id` | integer | Yes | Docket ID from a case search result |

**Returns:** Case name, court, dates (filed/terminated), assigned judge, cause, nature of suit, jury demand, docket number, and CourtListener URL.

---

### find_citing_cases

Find cases that cite a specific opinion — trace how a ruling has been used in later decisions.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `opinion_id` | integer | Yes | Opinion ID to find citing cases for |

**Returns:** Total count and up to 20 citing opinions with depth information.

---

### find_cited_cases

Find cases that an opinion relies on — understand the legal foundation of a decision.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `opinion_id` | integer | Yes | Opinion ID to find cited cases for |

**Returns:** Total count and up to 20 cited opinions with depth information.

---

### parse_legal_citations

Parse Bluebook-format legal citations from any text.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `text` | string | Yes | Text containing legal citations |

**Example:**
```
"Parse: See Brown v. Board, 347 U.S. 483 (1954); Miranda, 384 U.S. 436 (1966)."
```

**Returns:** Number of citations found, with each parsed into volume, reporter, page, court, year, and pin cite.

---

### list_available_courts

List all available US courts and their short codes for filtering searches.

**Parameters:** None

**Returns:** List of 400+ courts with ID, short name, full name, and jurisdiction type.

---

### list_reporter_abbreviations

List common legal reporter abbreviations and which courts they cover.

**Parameters:** None

**Returns:** Dictionary mapping abbreviations (e.g., "U.S.", "F.3d", "S. Ct.") to court descriptions.

---

## Clio Practice Management Tools (Pro)

All Clio tools require the `CLIO_TOKEN` environment variable.

### search_clients

Search for clients and contacts in Clio.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `query` | string | No | Search by name, email, or phone |
| `contact_type` | string | No | `Person` or `Company` |

**Returns:** Matching contacts with ID, name, type, email addresses, and phone numbers.

---

### search_matters

Search for matters (cases) in Clio.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `query` | string | No | Search by matter number or description |
| `status` | string | No | `Open`, `Closed`, or `Pending` |
| `client_id` | integer | No | Filter by client contact ID |

**Returns:** Matters with ID, display number, description, status, client, practice area, and dates.

---

### get_matter_details

Get full details of a specific matter from Clio.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `matter_id` | integer | Yes | The Clio matter ID |

**Returns:** Complete matter info including client, practice area, responsible attorney, billing method, statute of limitations, and custom fields.

---

### get_time_entries

Get billable hours from Clio, filterable by matter and date range.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `matter_id` | integer | No | Filter by matter ID |
| `date_from` | string | No | Start date (YYYY-MM-DD) |
| `date_to` | string | No | End date (YYYY-MM-DD) |

**Returns:** Time entries with date, quantity (hours), note, matter, user, activity description, and total amount.

---

### get_matter_tasks

Get tasks associated with a matter in Clio.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `matter_id` | integer | No | Filter by matter ID |
| `status` | string | No | `Complete` or `Incomplete` |

**Returns:** Tasks with name, description, status, due date, matter, assignee, and priority.

---

### get_matter_documents

Search documents in Clio.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `matter_id` | integer | No | Filter by matter ID |
| `query` | string | No | Search by document name |

**Returns:** Documents with name, content type, creation/update dates, matter, and latest version info.

---

### get_calendar

Get calendar entries (hearings, deadlines, meetings) from Clio.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `date_from` | string | No | Start date (YYYY-MM-DD) |
| `date_to` | string | No | End date (YYYY-MM-DD) |
| `matter_id` | integer | No | Filter by matter ID |

**Returns:** Calendar entries with summary, description, start/end times, location, matter, and attendees.

---

## PACER Court Filings Tools (Pro)

All PACER tools require `PACER_USERNAME` and `PACER_PASSWORD` environment variables.

**Note:** PACER charges $0.10/page for document downloads. Search and docket listing are free.

### search_federal_cases

Search PACER for federal court cases.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `case_name` | string | No | Party name or case title |
| `case_number` | string | No | Case number (e.g., "1:23-cv-01234") |
| `court_id` | string | No | Court code (e.g., `nysd`, `cacd`) |
| `date_filed_from` | string | No | Start date (MM/DD/YYYY) |
| `date_filed_to` | string | No | End date (MM/DD/YYYY) |

**Returns:** Matching federal cases with case details.

---

### get_federal_case

Get details of a specific federal case from PACER.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `case_id` | string | Yes | The PACER case ID |
| `court_id` | string | Yes | The court code |

**Returns:** Full case details from PACER.

---

### get_court_filings

Get docket entries (individual filings) for a federal case.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `case_id` | string | Yes | The PACER case ID |
| `court_id` | string | Yes | The court code |
| `date_from` | string | No | Start date (MM/DD/YYYY) |
| `date_to` | string | No | End date (MM/DD/YYYY) |

**Returns:** Docket entries showing motions, orders, briefs, and other filings.

---

## MCP Resources

### legal://courts/federal

Static guide to the US federal court system hierarchy — Supreme Court, Circuit Courts, District Courts, Bankruptcy Courts, and Specialized Courts with their codes.

### legal://citation-guide

Quick reference for reading Bluebook-format legal citations with examples.
