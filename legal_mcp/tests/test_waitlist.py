"""Tests for the waitlist API."""

import os
import sqlite3
import pytest
from fastapi.testclient import TestClient

# Override DB path before import
os.environ["WAITLIST_DB_TEST"] = "1"

from landing.api.waitlist import app, DB_PATH


@pytest.fixture(autouse=True)
def clean_db(tmp_path, monkeypatch):
    """Use a temp database for each test."""
    test_db = tmp_path / "test_waitlist.db"
    import landing.api.waitlist as wl
    monkeypatch.setattr(wl, "DB_PATH", test_db)
    yield
    if test_db.exists():
        test_db.unlink()


@pytest.fixture
def client():
    return TestClient(app)


def test_join_waitlist(client):
    resp = client.post("/api/waitlist", json={"email": "test@lawfirm.com"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["position"] == 1


def test_join_waitlist_with_plan(client):
    resp = client.post("/api/waitlist", json={"email": "pro@lawfirm.com", "plan": "pro"})
    assert resp.status_code == 200
    assert resp.json()["success"] is True


def test_duplicate_email(client):
    client.post("/api/waitlist", json={"email": "dup@lawfirm.com"})
    resp = client.post("/api/waitlist", json={"email": "dup@lawfirm.com"})
    assert resp.status_code == 200
    assert "already" in resp.json()["message"].lower()


def test_invalid_email(client):
    resp = client.post("/api/waitlist", json={"email": "not-an-email"})
    assert resp.status_code == 422


def test_waitlist_count(client):
    client.post("/api/waitlist", json={"email": "a@law.com"})
    client.post("/api/waitlist", json={"email": "b@law.com"})
    resp = client.get("/api/waitlist/count")
    assert resp.json()["count"] == 2
