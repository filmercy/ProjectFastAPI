"""Tests for the /api/v1/maintenance/ endpoints.

Every maintenance record requires a user, a client, and a racket to exist first.
- The user is seeded directly into the DB (seeded_user fixture) because there
  is no public registration endpoint — the router hardcodes DEFAULT_USER_ID.
- The client and racket are created through the API (maint_setup fixture).
"""
import pytest_asyncio

MAINT = "/api/v1/maintenance"


# ── fixture ───────────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def maint_setup(api_client, seeded_user):
    """Returns a dict with a valid client_id and racket_id ready for use."""
    client_resp = await api_client.post("/api/v1/clients/", json={
        "first_name": "Test", "last_name": "Player", "phone_number": "999"
    })
    assert client_resp.status_code == 201
    client_id = client_resp.json()["id"]

    racket_resp = await api_client.post("/api/v1/rackets/", json={
        "client_id": client_id,
        "brand": "Wilson",
        "model": "Pro Staff 97",
        "grip_size": "4 1/4",
    })
    assert racket_resp.status_code == 201
    racket_id = racket_resp.json()["id"]

    return {"client_id": client_id, "racket_id": racket_id}


# ── list ──────────────────────────────────────────────────────────────────────

async def test_list_empty(api_client):
    resp = await api_client.get(f"{MAINT}/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["items"] == []
    assert body["total"] == 0


# ── create ────────────────────────────────────────────────────────────────────

async def test_create_minimal(api_client, maint_setup):
    resp = await api_client.post(f"{MAINT}/", json={
        "client_racket_id": maint_setup["racket_id"],
        "service_type": "stringing",
        "service_cost": 25.00,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["service_type"] == "stringing"
    assert float(data["service_cost"]) == 25.00
    assert data["client_racket_id"] == maint_setup["racket_id"]
    assert "id" in data
    assert "service_date" in data


async def test_create_with_full_string_info(api_client, maint_setup):
    resp = await api_client.post(f"{MAINT}/", json={
        "client_racket_id": maint_setup["racket_id"],
        "service_type": "stringing",
        "service_cost": 30.00,
        "main_tension_kg": 24.5,
        "cross_tension_kg": 23.0,
        "duration_minutes": 45,
        "notes": "Customer requested high tension",
        "is_warranty_service": False,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert float(data["main_tension_kg"]) == 24.5
    assert float(data["cross_tension_kg"]) == 23.0
    assert data["duration_minutes"] == 45
    assert data["notes"] == "Customer requested high tension"


async def test_create_warranty_service(api_client, maint_setup):
    resp = await api_client.post(f"{MAINT}/", json={
        "client_racket_id": maint_setup["racket_id"],
        "service_type": "repair",
        "service_cost": 0.00,
        "is_warranty_service": True,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["is_warranty_service"] is True
    assert float(data["service_cost"]) == 0.00


async def test_create_invalid_racket(api_client, seeded_user):
    resp = await api_client.post(f"{MAINT}/", json={
        "client_racket_id": "00000000-0000-0000-0000-000000000000",
        "service_type": "stringing",
        "service_cost": 20.00,
    })
    assert resp.status_code == 404


async def test_create_missing_required_field(api_client, maint_setup):
    # service_cost is required
    resp = await api_client.post(f"{MAINT}/", json={
        "client_racket_id": maint_setup["racket_id"],
        "service_type": "stringing",
    })
    assert resp.status_code == 422


# ── get ───────────────────────────────────────────────────────────────────────

async def test_get_by_id(api_client, maint_setup):
    create_resp = await api_client.post(f"{MAINT}/", json={
        "client_racket_id": maint_setup["racket_id"],
        "service_type": "repair",
        "service_cost": 15.00,
    })
    record_id = create_resp.json()["id"]

    resp = await api_client.get(f"{MAINT}/{record_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == record_id


async def test_get_not_found(api_client):
    resp = await api_client.get(f"{MAINT}/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


# ── update ────────────────────────────────────────────────────────────────────

async def test_update_cost_and_notes(api_client, maint_setup):
    create_resp = await api_client.post(f"{MAINT}/", json={
        "client_racket_id": maint_setup["racket_id"],
        "service_type": "stringing",
        "service_cost": 20.00,
    })
    record_id = create_resp.json()["id"]

    resp = await api_client.put(f"{MAINT}/{record_id}", json={
        "service_cost": 25.00,
        "notes": "Updated after job",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert float(data["service_cost"]) == 25.00
    assert data["notes"] == "Updated after job"
    # untouched field unchanged
    assert data["service_type"] == "stringing"


async def test_update_not_found(api_client):
    resp = await api_client.put(
        f"{MAINT}/00000000-0000-0000-0000-000000000000",
        json={"service_cost": 10.00},
    )
    assert resp.status_code == 404


# ── delete ────────────────────────────────────────────────────────────────────

async def test_delete(api_client, maint_setup):
    create_resp = await api_client.post(f"{MAINT}/", json={
        "client_racket_id": maint_setup["racket_id"],
        "service_type": "other",
        "service_cost": 5.00,
    })
    record_id = create_resp.json()["id"]

    resp = await api_client.delete(f"{MAINT}/{record_id}")
    assert resp.status_code == 204

    # Hard delete — record is gone
    resp = await api_client.get(f"{MAINT}/{record_id}")
    assert resp.status_code == 404


async def test_delete_not_found(api_client):
    resp = await api_client.delete(f"{MAINT}/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


# ── filters ───────────────────────────────────────────────────────────────────

async def test_filter_by_racket(api_client, maint_setup):
    racket_id = maint_setup["racket_id"]

    await api_client.post(f"{MAINT}/", json={
        "client_racket_id": racket_id, "service_type": "stringing", "service_cost": 20.00
    })
    await api_client.post(f"{MAINT}/", json={
        "client_racket_id": racket_id, "service_type": "repair", "service_cost": 10.00
    })

    resp = await api_client.get(f"{MAINT}/?client_racket_id={racket_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert all(j["client_racket_id"] == racket_id for j in data["items"])


async def test_filter_by_service_type(api_client, maint_setup):
    racket_id = maint_setup["racket_id"]

    await api_client.post(f"{MAINT}/", json={
        "client_racket_id": racket_id, "service_type": "stringing", "service_cost": 20.00
    })
    await api_client.post(f"{MAINT}/", json={
        "client_racket_id": racket_id, "service_type": "repair", "service_cost": 10.00
    })

    resp = await api_client.get(f"{MAINT}/?service_type=stringing")
    assert resp.status_code == 200
    data = resp.json()
    assert all(j["service_type"] == "stringing" for j in data["items"])
