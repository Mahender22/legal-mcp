import os

COURTLISTENER_API_URL = "https://www.courtlistener.com/api/rest/v4"
COURTLISTENER_TOKEN = os.environ.get("COURTLISTENER_TOKEN", "")

CLIO_API_URL = "https://app.clio.com/api/v4"
CLIO_TOKEN = os.environ.get("CLIO_TOKEN", "")

PACER_API_URL = "https://pcl.uscourts.gov/pcl-public-api/rest"
PACER_USERNAME = os.environ.get("PACER_USERNAME", "")
PACER_PASSWORD = os.environ.get("PACER_PASSWORD", "")
# Optional: base32 TOTP secret for MFA-enrolled (upgraded) PACER accounts.
PACER_TOTP_SECRET = os.environ.get("PACER_TOTP_SECRET", "")

DEMO_MODE = os.environ.get("LEGAL_MCP_DEMO", "").lower() in ("1", "true", "yes")
