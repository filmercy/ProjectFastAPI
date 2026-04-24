"""Tests for /api/v1/categories/ and /api/v1/products/ endpoints."""

CAT = "/api/v1/categories"
PROD = "/api/v1/products"


# ── helpers ──────────────────────────────────────────────────────────────────

async def make_category(api_client, name="Strings", slug="strings"):
    resp = await api_client.post(f"{CAT}/", json={"name": name, "slug": slug})
    assert resp.status_code == 201
    return resp.json()


async def make_product(api_client, category_id, name="ALU Power", brand="Luxilon"):
    resp = await api_client.post(f"{PROD}/", json={
        "name": name, "brand": brand,
        "category_id": category_id, "price": 18.99,
    })
    assert resp.status_code == 201
    return resp.json()


# ── category tests ────────────────────────────────────────────────────────────

async def test_list_categories_empty(api_client):
    resp = await api_client.get(f"{CAT}/")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_create_category(api_client):
    resp = await api_client.post(f"{CAT}/", json={
        "name": "Strings", "slug": "strings", "description": "Tennis strings"
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Strings"
    assert data["slug"] == "strings"
    assert "id" in data


async def test_create_category_missing_slug(api_client):
    resp = await api_client.post(f"{CAT}/", json={"name": "Strings"})
    assert resp.status_code == 422


async def test_get_category(api_client):
    cat = await make_category(api_client)
    resp = await api_client.get(f"{CAT}/{cat['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == cat["id"]


async def test_get_category_not_found(api_client):
    resp = await api_client.get(f"{CAT}/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


# ── product tests ─────────────────────────────────────────────────────────────

async def test_list_products_empty(api_client):
    resp = await api_client.get(f"{PROD}/")
    assert resp.status_code == 200
    assert resp.json()["items"] == []


async def test_create_product(api_client):
    cat = await make_category(api_client)
    resp = await api_client.post(f"{PROD}/", json={
        "name": "ALU Power 125",
        "brand": "Luxilon",
        "category_id": cat["id"],
        "price": 18.99,
        "quantity_in_stock": 10,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "ALU Power 125"
    assert data["category_id"] == cat["id"]
    assert data["is_active"] is True
    assert data["quantity_in_stock"] == 10


async def test_create_product_invalid_category(api_client):
    resp = await api_client.post(f"{PROD}/", json={
        "name": "Ghost String", "brand": "Ghost",
        "category_id": "00000000-0000-0000-0000-000000000000",
    })
    assert resp.status_code == 404


async def test_get_product(api_client):
    cat = await make_category(api_client)
    prod = await make_product(api_client, cat["id"])

    resp = await api_client.get(f"{PROD}/{prod['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == prod["id"]


async def test_get_product_not_found(api_client):
    resp = await api_client.get(f"{PROD}/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


async def test_update_product_price(api_client):
    cat = await make_category(api_client)
    prod = await make_product(api_client, cat["id"])

    resp = await api_client.put(f"{PROD}/{prod['id']}", json={"price": 22.50})
    assert resp.status_code == 200
    data = resp.json()
    assert float(data["price"]) == 22.50
    assert data["name"] == prod["name"]  # other fields unchanged


async def test_update_product_stock(api_client):
    cat = await make_category(api_client)
    prod = await make_product(api_client, cat["id"])

    resp = await api_client.put(f"{PROD}/{prod['id']}", json={"quantity_in_stock": 50})
    assert resp.status_code == 200
    assert resp.json()["quantity_in_stock"] == 50


async def test_deactivate_product(api_client):
    cat = await make_category(api_client)
    prod = await make_product(api_client, cat["id"])

    resp = await api_client.delete(f"{PROD}/{prod['id']}")
    assert resp.status_code == 204

    # Soft-deleted: still retrievable but inactive
    resp = await api_client.get(f"{PROD}/{prod['id']}")
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


async def test_filter_products_by_category(api_client):
    cat_strings = await make_category(api_client, "Strings", "strings")
    cat_grips = await make_category(api_client, "Grips", "grips")
    await make_product(api_client, cat_strings["id"], "ALU Power", "Luxilon")
    await make_product(api_client, cat_grips["id"], "Pro Overgrip", "Wilson")

    resp = await api_client.get(f"{PROD}/?category_id={cat_strings['id']}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "ALU Power"
