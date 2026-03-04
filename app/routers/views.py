"""HTML view routes — renders Jinja2 templates for the dashboard UI."""
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.client import Client
from app.models.product import Product
from app.models.product_category import ProductCategory
from app.models.maintenance_record import MaintenanceRecord
from app.models.client_racket import ClientRacket

router = APIRouter(tags=["Views"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard")
async def dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    total_clients = (await db.execute(select(func.count(Client.id)))).scalar()
    total_products = (await db.execute(select(func.count(Product.id)))).scalar()
    total_categories = (await db.execute(select(func.count(ProductCategory.id)))).scalar()
    total_services = (await db.execute(select(func.count(MaintenanceRecord.id)))).scalar()

    recent_records = (await db.execute(
        select(MaintenanceRecord).order_by(MaintenanceRecord.service_date.desc()).limit(5)
    )).scalars().all()

    recent_maintenance = []
    for record in recent_records:
        racket = (await db.execute(
            select(ClientRacket).where(ClientRacket.id == record.client_racket_id)
        )).scalar_one_or_none()
        client = (await db.execute(
            select(Client).where(Client.id == racket.client_id)
        )).scalar_one_or_none() if racket else None
        recent_maintenance.append({
            "client_id": client.id if client else None,
            "client_name": f"{client.first_name} {client.last_name}" if client else "Unknown",
            "racket_info": f"{racket.brand} {racket.model}" if racket else "Unknown",
            "service_type": record.service_type,
            "service_date": record.service_date.strftime("%Y-%m-%d") if record.service_date else "-",
        })

    return templates.TemplateResponse("pages/dashboard.html", {
        "request": request,
        "active_page": "dashboard",
        "stats": {
            "total_clients": total_clients,
            "total_products": total_products,
            "total_categories": total_categories,
            "total_services": total_services,
        },
        "recent_maintenance": recent_maintenance,
    })


@router.get("/clients")
async def clients_page(request: Request, db: AsyncSession = Depends(get_db)):
    clients = (await db.execute(
        select(Client).where(Client.is_active == True).order_by(Client.last_name)
    )).scalars().all()
    return templates.TemplateResponse("pages/clients.html", {
        "request": request,
        "active_page": "clients",
        "clients": [
            {
                "id": c.id,
                "first_name": c.first_name,
                "last_name": c.last_name,
                "email": c.email,
                "phone_number": c.phone_number,
                "date_of_birth": c.date_of_birth.isoformat() if c.date_of_birth else None,
                "address_line1": c.address_line1,
                "address_line2": c.address_line2,
                "city": c.city,
                "postal_code": c.postal_code,
                "country": c.country,
                "notes": c.notes,
                "is_active": c.is_active,
                "created_at": c.created_at.strftime("%Y-%m-%d") if c.created_at else "-",
            }
            for c in clients
        ],
    })


@router.get("/clients/{client_id}")
async def client_detail(client_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    client = (await db.execute(
        select(Client).where(Client.id == client_id)
    )).scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    rackets = (await db.execute(
        select(ClientRacket).where(ClientRacket.client_id == client_id).order_by(ClientRacket.brand)
    )).scalars().all()

    return templates.TemplateResponse("pages/client_detail.html", {
        "request": request,
        "active_page": "clients",
        "client": {
            "id": client.id,
            "first_name": client.first_name,
            "last_name": client.last_name,
            "email": client.email,
            "phone_number": client.phone_number,
            "date_of_birth": client.date_of_birth.isoformat() if client.date_of_birth else None,
            "address_line1": client.address_line1,
            "address_line2": client.address_line2,
            "city": client.city,
            "postal_code": client.postal_code,
            "country": client.country,
            "notes": client.notes,
            "is_active": client.is_active,
            "created_at": client.created_at.strftime("%Y-%m-%d") if client.created_at else "-",
        },
        "rackets": [
            {
                "id": r.id,
                "brand": r.brand,
                "model": r.model,
                "grip_size": r.grip_size,
                "custom_name": r.custom_name,
                "purchase_date": r.purchase_date.isoformat() if r.purchase_date else None,
                "notes": r.notes,
                "is_active": r.is_active,
            }
            for r in rackets
        ],
    })


@router.get("/products")
async def products_page(request: Request, db: AsyncSession = Depends(get_db)):
    products = (await db.execute(select(Product).where(Product.is_active == True).order_by(Product.name))).scalars().all()
    cats = (await db.execute(select(ProductCategory).order_by(ProductCategory.name))).scalars().all()
    categories_map = {c.id: c.name for c in cats}
    return templates.TemplateResponse("pages/products.html", {
        "request": request,
        "active_page": "products",
        "categories": [{"id": c.id, "name": c.name} for c in cats],
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "brand": p.brand,
                "model": p.model,
                "sku": p.sku,
                "description": p.description,
                "price": float(p.price) if p.price is not None else None,
                "cost_price": float(p.cost_price) if p.cost_price is not None else None,
                "quantity_in_stock": p.quantity_in_stock,
                "category_id": p.category_id,
                "category_name": categories_map.get(p.category_id),
                "is_active": p.is_active,
            }
            for p in products
        ],
    })


@router.get("/categories")
async def categories_page(request: Request, db: AsyncSession = Depends(get_db)):
    categories = (await db.execute(select(ProductCategory).where(ProductCategory.is_active == True).order_by(ProductCategory.name))).scalars().all()
    return templates.TemplateResponse("pages/categories.html", {
        "request": request,
        "active_page": "categories",
        "categories": [{"name": c.name, "description": c.description} for c in categories],
    })


@router.get("/maintenance")
async def maintenance_page(request: Request, db: AsyncSession = Depends(get_db)):
    records = (await db.execute(
        select(MaintenanceRecord).order_by(MaintenanceRecord.service_date.desc())
    )).scalars().all()

    # Bulk lookups to avoid N+1 queries
    all_products = (await db.execute(
        select(Product).where(Product.is_active == True).order_by(Product.name)
    )).scalars().all()
    products_map = {p.id: p.name for p in all_products}

    strings_category_id = (await db.execute(
        select(ProductCategory.id).where(ProductCategory.name.ilike("%string%"))
    )).scalar_one_or_none()
    strings_for_dropdown = [
        {"id": p.id, "label": f"{p.brand} — {p.name}"}
        for p in all_products if p.category_id == strings_category_id
    ]
    

    all_rackets = (await db.execute(
        select(ClientRacket).where(ClientRacket.is_active == True).order_by(ClientRacket.brand)
    )).scalars().all()
    rackets_by_id = {r.id: r for r in all_rackets}

    all_clients = (await db.execute(select(Client))).scalars().all()
    clients_map = {c.id: f"{c.first_name} {c.last_name}" for c in all_clients}

    rackets_for_dropdown = [
        {"id": r.id, "label": f"{clients_map.get(r.client_id, 'Unknown')} — {r.brand} {r.model}"}
        for r in all_rackets
    ]

    jobs = []
    for record in records:
        racket = rackets_by_id.get(record.client_racket_id)
        client_name = clients_map.get(racket.client_id, "Unknown") if racket else "Unknown"
        racket_info = f"{racket.brand} {racket.model}" if racket else "Unknown"

        main_string_name = products_map.get(record.main_string_id) if record.main_string_id else None
        cross_string_name = products_map.get(record.cross_string_id) if record.cross_string_id else None
        string_info = main_string_name or "-"
        if cross_string_name and cross_string_name != main_string_name:
            string_info = f"{main_string_name} / {cross_string_name}"

        stype = record.service_type
        if hasattr(stype, 'value'):
            stype = stype.value

        jobs.append({
            "id": record.id,
            "client_name": client_name,
            "racket_info": racket_info,
            "string_info": string_info,
            "client_racket_id": record.client_racket_id,
            "service_type": stype,
            "main_string_id": record.main_string_id,
            "cross_string_id": record.cross_string_id,
            "main_tension_kg": float(record.main_tension_kg) if record.main_tension_kg is not None else None,
            "cross_tension_kg": float(record.cross_tension_kg) if record.cross_tension_kg is not None else None,
            "string_pattern": record.string_pattern,
            "base_grip_id": record.base_grip_id,
            "overgrip_id": record.overgrip_id,
            "number_of_overgrips": record.number_of_overgrips,
            "dampener_id": record.dampener_id,
            "dampener_position": record.dampener_position,
            "service_cost": float(record.service_cost) if record.service_cost is not None else None,
            "duration_minutes": record.duration_minutes,
            "notes": record.notes,
            "is_warranty_service": record.is_warranty_service,
            "next_service_due_date": record.next_service_due_date.isoformat() if record.next_service_due_date else None,
            "service_date": record.service_date.strftime("%Y-%m-%d") if record.service_date else "-",
        })

    all_products_for_dropdown = [
        {"id": p.id, "label": f"{p.brand} — {p.name}"}
        for p in all_products
    ]

    return templates.TemplateResponse("pages/maintenance.html", {
        "request": request,
        "active_page": "maintenance",
        "jobs": jobs,
        "rackets_for_dropdown": rackets_for_dropdown,
        "strings_for_dropdown": strings_for_dropdown,
        "products_for_dropdown": all_products_for_dropdown,
    })
