"""Tests for the /api/v1/clients/ endpoints."""

BASE = "/api/v1/clients"


async def test_list_empty(api_client):
    resp = await api_client.get(f"{BASE}/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["items"] == []
    assert body["total"] == 0


async def test_create(api_client):
    resp = await api_client.post(f"{BASE}/", json={
        "first_name": "Mario",
        "last_name": "Rossi",
        "phone_number": "+39 333 1234567",
        "email": "mario@test.com",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["first_name"] == "Mario"
    assert data["last_name"] == "Rossi"
    assert data["is_active"] is True
    assert "id" in data


async def test_create_missing_required_field(api_client):
    # phone_number is required
    resp = await api_client.post(f"{BASE}/", json={
        "first_name": "Mario",
        "last_name": "Rossi",
    })
    assert resp.status_code == 422


async def test_get_by_id(api_client):
    create_resp = await api_client.post(f"{BASE}/", json={
        "first_name": "Anna", "last_name": "Verdi", "phone_number": "123"
    })
    client_id = create_resp.json()["id"]

    resp = await api_client.get(f"{BASE}/{client_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == client_id


async def test_get_not_found(api_client):
    resp = await api_client.get(f"{BASE}/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


async def test_update(api_client):
    create_resp = await api_client.post(f"{BASE}/", json={
        "first_name": "Luca", "last_name": "Bianchi", "phone_number": "456"
    })
    client_id = create_resp.json()["id"]

    resp = await api_client.put(f"{BASE}/{client_id}", json={"phone_number": "789"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["phone_number"] == "789"
    assert data["first_name"] == "Luca"  # unchanged fields stay


async def test_update_not_found(api_client):
    resp = await api_client.put(
        f"{BASE}/00000000-0000-0000-0000-000000000000",
        json={"phone_number": "000"},
    )
    assert resp.status_code == 404


async def test_soft_delete(api_client):
    create_resp = await api_client.post(f"{BASE}/", json={
        "first_name": "Delete", "last_name": "Me", "phone_number": "000"
    })
    client_id = create_resp.json()["id"]

    resp = await api_client.delete(f"{BASE}/{client_id}")
    assert resp.status_code == 204

    # Record still exists but is deactivated
    resp = await api_client.get(f"{BASE}/{client_id}")
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


async def test_delete_not_found(api_client):
    resp = await api_client.delete(f"{BASE}/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


async def test_search_by_name(api_client):
    await api_client.post(f"{BASE}/", json={"first_name": "Federer", "last_name": "Roger", "phone_number": "1"})
    await api_client.post(f"{BASE}/", json={"first_name": "Nadal", "last_name": "Rafael", "phone_number": "2"})

    resp = await api_client.get(f"{BASE}/?search=federer")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["first_name"] == "Federer"


async def test_filter_active(api_client):
    active_resp = await api_client.post(f"{BASE}/", json={
        "first_name": "Active", "last_name": "One", "phone_number": "1"
    })
    inactive_resp = await api_client.post(f"{BASE}/", json={
        "first_name": "Inactive", "last_name": "One", "phone_number": "2"
    })
    await api_client.delete(f"{BASE}/{inactive_resp.json()['id']}")

    resp = await api_client.get(f"{BASE}/?is_active=true")
    assert resp.status_code == 200
    active_ids = [c["id"] for c in resp.json()["items"]]
    assert active_resp.json()["id"] in active_ids
    assert inactive_resp.json()["id"] not in active_ids


async def test_pagination(api_client):
    for i in range(5):
        await api_client.post(f"{BASE}/", json={
            "first_name": f"Client{i}", "last_name": "Test", "phone_number": str(i)
        })

    resp = await api_client.get(f"{BASE}/?page=1&limit=3")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 3
    assert data["total"] == 5
