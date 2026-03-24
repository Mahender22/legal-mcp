# LegalMCP Setup Guide

This guide walks you through getting API credentials for each LegalMCP integration.

## 1. CourtListener (Free — Starter + Pro)

CourtListener provides access to 4M+ US court opinions. Works without a token, but you'll get higher rate limits with one.

### Get Your Token

1. Go to [courtlistener.com](https://www.courtlistener.com/sign-in/)
2. Create a free account (email + password)
3. Go to your profile: **Settings → API Tokens**
4. Click **Create Token**
5. Copy the token

### Configure

```bash
export COURTLISTENER_TOKEN="your-token-here"
```

Or add to your `.env` file:
```
COURTLISTENER_TOKEN=your-token-here
```

### Verify

```bash
# Test with curl
curl -H "Authorization: Token YOUR_TOKEN" \
  "https://www.courtlistener.com/api/rest/v4/search/?type=o&q=test"
```

If you get JSON results, you're set.

---

## 2. Clio Practice Management (Pro Plan)

Clio integration lets your AI access contacts, matters, billing, documents, and calendar.

### Get Your OAuth Token

1. Go to [developer.clio.com](https://developer.clio.com)
2. Sign in with your Clio account
3. Click **Applications → Add Application**
4. Fill in:
   - **Name**: LegalMCP
   - **Redirect URI**: `http://localhost:3000/callback`
   - **Scopes**: Select all read scopes you need (contacts, matters, activities, documents, calendar_entries)
5. Note your **Client ID** and **Client Secret**
6. Follow [Clio's OAuth flow](https://app.clio.com/api/v4/documentation#section/Authorization) to get an access token

### Configure

```bash
export CLIO_TOKEN="your-oauth-access-token"
```

### Verify

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://app.clio.com/api/v4/contacts.json?limit=1"
```

### Notes

- Clio tokens expire — you'll need to refresh them periodically
- Only read operations are supported (LegalMCP never writes to Clio)
- Data stays local — LegalMCP runs on your machine, nothing is sent to external servers

---

## 3. PACER Federal Court Filings (Pro Plan)

PACER provides access to federal court case filings and docket entries.

### Important: PACER Costs Money

PACER charges **$0.10 per page** for document access. Case searches and docket lookups are free, but downloading actual filings costs money. LegalMCP's tools primarily search and list — they don't automatically download paid documents.

### Get Your Account

1. Go to [pacer.uscourts.gov](https://pacer.uscourts.gov)
2. Click **Register for an Account**
3. Choose **PACER Case Search Only** (sufficient for LegalMCP)
4. Fill in the registration form
5. You'll receive login credentials by email

### Configure

```bash
export PACER_USERNAME="your-username"
export PACER_PASSWORD="your-password"
```

### Verify

Your PACER credentials will be tested automatically when LegalMCP makes its first PACER request.

---

## Demo Mode (No API Keys)

Want to try LegalMCP without setting up any API keys? Use demo mode:

```bash
export LEGAL_MCP_DEMO=true
legal-mcp
```

Demo mode returns pre-cached results from famous US Supreme Court cases. Great for testing your setup and exploring what LegalMCP can do.

---

## Troubleshooting

### "CourtListener authentication failed"
- Check that `COURTLISTENER_TOKEN` is set correctly
- Tokens don't expire, but make sure there are no extra spaces
- Try generating a new token at courtlistener.com

### "Clio API token not set"
- Ensure `CLIO_TOKEN` is set in your environment
- Clio tokens expire — regenerate if your token is old

### "PACER credentials not set"
- Both `PACER_USERNAME` and `PACER_PASSWORD` must be set
- PACER accounts can take 24-48 hours to activate after registration

### "rate limit exceeded"
- CourtListener: Add a token for higher limits, or wait 30 seconds
- Clio: Standard rate limits apply per your Clio plan
- PACER: Very generous limits, but slow down if you see 429 errors

### "Cannot connect to [service]"
- Check your internet connection
- The service may be temporarily down — try again in a few minutes
