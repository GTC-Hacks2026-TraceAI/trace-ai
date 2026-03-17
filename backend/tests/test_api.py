"""Tests for Trace AI API endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app import store


@pytest.fixture(autouse=True)
def _clear_store():
    """Reset the case repository between tests."""
    store.case_repository.clear()
    yield
    store.case_repository.clear()


@pytest.fixture
def client():
    return TestClient(app)


# ── Health ──────────────────────────────────────────────────────────────

def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


# ── Cases ───────────────────────────────────────────────────────────────

def test_create_case(client):
    payload = {
        "subject_name": "Jane Doe",
        "description": "Female, approx 25, brown hair",
        "last_known_location": "Building A lobby",
        "clothing": "Red jacket, blue jeans",
    }
    resp = client.post("/cases", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["subject_name"] == "Jane Doe"
    assert body["status"] == "open"
    assert "id" in body
    assert "created_at" in body


def test_list_cases_empty(client):
    resp = client.get("/cases")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_cases(client):
    client.post("/cases", json={"subject_name": "Person A"})
    client.post("/cases", json={"subject_name": "Person B"})
    resp = client.get("/cases")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


# ── Get single case ──────────────────────────────────────────────────────

def test_get_case(client):
    create_resp = client.post("/cases", json={"subject_name": "Alice"})
    case_id = create_resp.json()["id"]
    resp = client.get(f"/cases/{case_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == case_id
    assert body["subject_name"] == "Alice"


def test_get_case_not_found(client):
    resp = client.get("/cases/nonexistent")
    assert resp.status_code == 404


# ── Search ──────────────────────────────────────────────────────────────

def test_search_case(client):
    create_resp = client.post("/cases", json={
        "subject_name": "Jane Doe",
        "description": "Brown hair",
        "clothing": "Red jacket",
    })
    case_id = create_resp.json()["id"]
    resp = client.post(f"/cases/{case_id}/search")
    assert resp.status_code == 200
    sightings = resp.json()
    assert len(sightings) >= 3
    # Sightings should be sorted by score descending
    scores = [s["similarity_score"] for s in sightings]
    assert scores == sorted(scores, reverse=True)
    # Each sighting has required fields
    for s in sightings:
        assert "camera_id" in s
        assert "frame_id" in s
        assert "timestamp" in s
        assert "similarity_score" in s
        assert "explanation" in s


def test_search_case_not_found(client):
    resp = client.post("/cases/nonexistent/search")
    assert resp.status_code == 404


# ── Timeline ────────────────────────────────────────────────────────────

def test_timeline_empty(client):
    create_resp = client.post("/cases", json={"subject_name": "Jane"})
    case_id = create_resp.json()["id"]
    resp = client.get(f"/cases/{case_id}/timeline")
    assert resp.status_code == 200
    body = resp.json()
    assert body["entries"] == []
    assert body["subject_name"] == "Jane"


def test_timeline_after_search(client):
    create_resp = client.post("/cases", json={
        "subject_name": "Jane Doe",
        "description": "Female, approx 25, brown hair",
        "last_known_location": "Building A lobby",
        "clothing": "Red jacket, blue jeans, black backpack",
    })
    case_id = create_resp.json()["id"]
    client.post(f"/cases/{case_id}/search")

    resp = client.get(f"/cases/{case_id}/timeline")
    assert resp.status_code == 200
    body = resp.json()
    entries = body["entries"]
    assert len(entries) >= 3
    # Entries should be sorted by timestamp
    timestamps = [e["timestamp"] for e in entries]
    assert timestamps == sorted(timestamps)
    # Timeline should include a summary
    assert "summary" in body
    assert isinstance(body["summary"], str)
    # Each entry should have enriched fields
    for e in entries:
        assert "camera_name" in e
        assert "location" in e
        assert "similarity_score" in e
        assert "explanation" in e


def test_timeline_case_not_found(client):
    resp = client.get("/cases/nonexistent/timeline")
    assert resp.status_code == 404


def test_create_case_missing_subject_name(client):
    """subject_name is required; omitting it must return 422."""
    resp = client.post("/cases", json={"description": "no name provided"})
    assert resp.status_code == 422


def test_create_case_minimal(client):
    """Only the required subject_name field should be enough to create a case."""
    resp = client.post("/cases", json={"subject_name": "John Smith"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["subject_name"] == "John Smith"
    assert body["status"] == "open"
    assert body["description"] is None
    assert body["clothing"] is None
    assert body["last_known_location"] is None


def test_health_service_field(client):
    """Health response must carry both 'status' and 'service' fields."""
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "trace-ai"


# ── Camera Recommendations ──────────────────────────────────────────────

def test_camera_recommendations_case_not_found(client):
    resp = client.get("/cases/nonexistent/camera-recommendations")
    assert resp.status_code == 404


def test_camera_recommendations_cold_start(client):
    create_resp = client.post("/cases", json={"subject_name": "Jane"})
    case_id = create_resp.json()["id"]
    resp = client.get(f"/cases/{case_id}/camera-recommendations")
    assert resp.status_code == 200
    recs = resp.json()
    assert len(recs) >= 1
    assert "reason" in recs[0]
    assert "priority" in recs[0]


def test_camera_recommendations_after_search(client):
    create_resp = client.post("/cases", json={"subject_name": "Jane Doe"})
    case_id = create_resp.json()["id"]
    client.post(f"/cases/{case_id}/search")

    resp = client.get(f"/cases/{case_id}/camera-recommendations")
    assert resp.status_code == 200
    recs = resp.json()
    # Should recommend cameras adjacent to sighting locations
    for rec in recs:
        assert "camera_id" in rec
        assert "reason" in rec
        assert rec["priority"] >= 1


# ── /recommendations alias ──────────────────────────────────────────────

def test_recommendations_alias_cold_start(client):
    create_resp = client.post("/cases", json={"subject_name": "Bob"})
    case_id = create_resp.json()["id"]
    resp = client.get(f"/cases/{case_id}/recommendations")
    assert resp.status_code == 200
    recs = resp.json()
    assert len(recs) >= 1
    assert "camera_id" in recs[0]
    assert "reason" in recs[0]
    assert recs[0]["priority"] >= 1


def test_recommendations_alias_not_found(client):
    resp = client.get("/cases/nonexistent/recommendations")
    assert resp.status_code == 404
