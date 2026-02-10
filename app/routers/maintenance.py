"""Maintenance records router for stringing history and services."""
from typing import Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, Query, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.maintenance_record import MaintenanceRecord, ServiceType
from app.models.client_racket import ClientRacket
from app.models.product import Product
from app.schemas.maintenance_record import (
    MaintenanceRecordCreate,
    MaintenanceRecordUpdate,
    MaintenanceRecordResponse
)
from app.utils.pagination import PaginatedResponse
from app.utils.exceptions import NotFoundException

router = APIRouter(prefix="/maintenance", tags=["Maintenance Records"])


@router.get("/", response_model=PaginatedResponse[MaintenanceRecordResponse])
async def list_maintenance_records(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    client_racket_id: Optional[str] = Query(None, description="Filter by racket UUID"),
    service_type: Optional[ServiceType] = Query(None, description="Filter by service type"),
    date_from: Optional[date] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db)
):
    """
    List all maintenance records with pagination and filters.

    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 20, max: 100)
    - **client_racket_id**: Filter by racket UUID
    - **service_type**: Filter by service type (stringing, repair, other)
    - **date_from**: Filter records from this date
    - **date_to**: Filter records up to this date
    """
    # Build query
    query = select(MaintenanceRecord)

    # Apply filters
    if client_racket_id:
        query = query.where(MaintenanceRecord.client_racket_id == client_racket_id)

    if service_type:
        query = query.where(MaintenanceRecord.service_type == service_type)

    if date_from:
        query = query.where(MaintenanceRecord.service_date >= datetime.combine(date_from, datetime.min.time()))

    if date_to:
        query = query.where(MaintenanceRecord.service_date <= datetime.combine(date_to, datetime.max.time()))

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(MaintenanceRecord.service_date.desc())

    # Execute query
    result = await db.execute(query)
    records = result.scalars().all()

    return PaginatedResponse.create(
        items=records,
        total=total,
        page=page,
        limit=limit
    )


@router.get("/{record_id}", response_model=MaintenanceRecordResponse)
async def get_maintenance_record(
    record_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific maintenance record by ID.

    - **record_id**: Maintenance record UUID
    """
    result = await db.execute(
        select(MaintenanceRecord).where(MaintenanceRecord.id == record_id)
    )
    record = result.scalar_one_or_none()

    if not record:
        raise NotFoundException(f"Maintenance record with ID {record_id} not found")

    return record


@router.post("/", response_model=MaintenanceRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_maintenance_record(
    record: MaintenanceRecordCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new maintenance record (perform stringing or service).

    **Required fields:**
    - **client_racket_id**: Racket UUID (required)
    - **service_type**: Type of service (stringing, repair, other)
    - **service_cost**: Cost of service

    **String Configuration (optional for stringing):**
    - **main_string_id**: Product UUID for main strings
    - **cross_string_id**: Product UUID for cross strings (can be different)
    - **main_tension_kg**: Main string tension in kg
    - **cross_tension_kg**: Cross string tension in kg
    - **string_pattern**: String pattern (e.g., "16x19")

    **Grip Configuration (optional):**
    - **base_grip_id**: Product UUID for base grip
    - **overgrip_id**: Product UUID for overgrip
    - **number_of_overgrips**: Number of overgrip layers (default: 1)

    **Accessories (optional):**
    - **dampener_id**: Product UUID for dampener
    - **dampener_position**: Position (e.g., "center", "bottom")

    **Additional:**
    - **notes**: Any special notes or observations
    - **is_warranty_service**: If this is a warranty service (default: false)
    - **next_service_due_date**: Estimated date for next service
    """
    # Verify racket exists
    racket_result = await db.execute(
        select(ClientRacket).where(ClientRacket.id == record.client_racket_id)
    )
    racket = racket_result.scalar_one_or_none()
    if not racket:
        raise NotFoundException(f"Racket with ID {record.client_racket_id} not found")

    # Verify all product IDs exist (strings, grips, dampener)
    product_ids = [
        record.main_string_id,
        record.cross_string_id,
        record.base_grip_id,
        record.overgrip_id,
        record.dampener_id
    ]
    product_ids = [pid for pid in product_ids if pid is not None]

    if product_ids:
        for product_id in product_ids:
            product_result = await db.execute(
                select(Product).where(Product.id == product_id)
            )
            if not product_result.scalar_one_or_none():
                raise NotFoundException(f"Product with ID {product_id} not found")

    # Create maintenance record
    # Auth disabled - using default admin user
    DEFAULT_USER_ID = "c4fa281e-11af-4510-82f6-509ae30ffc98"
    new_record = MaintenanceRecord(
        performed_by_user_id=DEFAULT_USER_ID,
        **record.model_dump()
    )

    db.add(new_record)

    # Optionally: Decrement stock for products used
    # This can be implemented later based on business needs

    await db.commit()
    await db.refresh(new_record)

    return new_record


@router.put("/{record_id}", response_model=MaintenanceRecordResponse)
async def update_maintenance_record(
    record_id: str,
    record: MaintenanceRecordUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing maintenance record.

    - **record_id**: Maintenance record UUID
    - Updates only provided fields
    """
    result = await db.execute(
        select(MaintenanceRecord).where(MaintenanceRecord.id == record_id)
    )
    record = result.scalar_one_or_none()

    if not record:
        raise NotFoundException(f"Maintenance record with ID {record_id} not found")

    # Update fields
    update_data = record.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)

    await db.commit()
    await db.refresh(record)

    return record


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_maintenance_record(
    record_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a maintenance record (admin only).

    - **record_id**: Maintenance record UUID

    Note: This permanently deletes the record. Use with caution.
    """
    result = await db.execute(
        select(MaintenanceRecord).where(MaintenanceRecord.id == record_id)
    )
    record = result.scalar_one_or_none()

    if not record:
        raise NotFoundException(f"Maintenance record with ID {record_id} not found")

    await db.delete(record)
    await db.commit()

    return None
