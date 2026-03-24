"""Waitlist API — collects emails for LegalMCP launch."""

import sqlite3
import re
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

DB_PATH = Path(__file__).parent / "waitlist.db"

app = FastAPI(title="LegalMCP Waitlist")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS waitlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            plan TEXT DEFAULT 'starter',
            created_at TEXT NOT NULL
        )"""
    )
    conn.commit()
    return conn


class WaitlistEntry(BaseModel):
    email: str
    plan: str = "starter"

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", v):
            raise ValueError("Invalid email address")
        return v

    @field_validator("plan")
    @classmethod
    def validate_plan(cls, v: str) -> str:
        if v not in ("starter", "pro"):
            raise ValueError("Plan must be 'starter' or 'pro'")
        return v


@app.post("/api/waitlist")
def join_waitlist(entry: WaitlistEntry):
    db = get_db()
    try:
        db.execute(
            "INSERT INTO waitlist (email, plan, created_at) VALUES (?, ?, ?)",
            (entry.email, entry.plan, datetime.now(timezone.utc).isoformat()),
        )
        db.commit()
        count = db.execute("SELECT COUNT(*) FROM waitlist").fetchone()[0]
        return {"success": True, "message": f"You're #{count} on the waitlist!", "position": count}
    except sqlite3.IntegrityError:
        return {"success": True, "message": "You're already on the waitlist!"}
    finally:
        db.close()


@app.get("/api/waitlist/count")
def waitlist_count():
    db = get_db()
    count = db.execute("SELECT COUNT(*) FROM waitlist").fetchone()[0]
    db.close()
    return {"count": count}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
