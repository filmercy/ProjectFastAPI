"""Client rackets router for managing rackets owned by clients."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.client_racket import ClientRacket
from app.models.client import Client
from app.schemas.client_racket import (
    ClientRacketCreate,
    ClientRacketUpdate,
    ClientRacketResponse
)
from app.utils.pagination import PaginatedResponse
from app.utils.exceptions import NotFoundException

router = APIRouter(prefix="/rackets", tags=["Client Rackets"])


@router.get("/", response_model=PaginatedResponse[ClientRacketResponse])
async def list_rackets(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    client_id: Optional[str] = Query(None, description="Filter by client UUID"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    List all client rackets with pagination and filters.

    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 20, max: 100)
    - **client_id**: Filter by client UUID
    - **brand**: Filter by racket brand
    - **is_active**: Filter by active status (client still owns it)
    """
    # Build query
    query = select(ClientRacket)

    # Apply filters
    if client_id:
        query = query.where(ClientRacket.client_id == client_id)

    if brand:
        query = query.where(ClientRacket.brand.ilike(f"%{brand}%"))

    if is_active is not None:
        query = query.where(ClientRacket.is_active == is_active)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(ClientRacket.brand, ClientRacket.model)

    # Execute query
    result = await db.execute(query)
    rackets = result.scalars().all()

    return PaginatedResponse.create(
        items=rackets,
        total=total,
        page=page,
        limit=limit
    )


@router.get("/{racket_id}", response_model=ClientRacketResponse)
async def get_racket(
    racket_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific racket by ID.

    - **racket_id**: Racket UUID
    """
    result = await db.execute(
        select(ClientRacket).where(ClientRacket.id == racket_id)
    )
    racket = result.scalar_one_or_none()

    if not racket:
        raise NotFoundException(f"Racket with ID {racket_id} not found")

    return racket


@router.post("/", response_model=ClientRacketResponse, status_code=status.HTTP_201_CREATED)
async def create_racket(
    racket_data: ClientRacketCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Add a new racket for a client.

    - **client_id**: Client UUID (required)
    - **brand**: Racket brand (required) - e.g., "Wilson", "Babolat"
    - **model**: Racket model (required) - e.g., "Pro Staff 97"
    - **grip_size**: Grip size (required) - e.g., "4 1/4", "4 3/8"
    - **custom_name**: Optional custom name - e.g., "My favorite racket"
    - **serial_number**: Optional serial number
    - **purchase_date**: Optional purchase date
    - **weight_unstrung**: Optional weight in grams
    - **notes**: Any special notes about the racket
    """
    # Verify client exists
    client_result = await db.execute(
        select(Client).where(Client.id == racket_data.client_id)
    )
    if not client_result.scalar_one_or_none():
        raise NotFoundException(f"Client with ID {racket_data.client_id} not found")

    new_racket = ClientRacket(**racket_data.model_dump())

    db.add(new_racket)
    await db.commit()
    await db.refresh(new_racket)

    return new_racket


@router.put("/{racket_id}", response_model=ClientRacketResponse)
async def update_racket(
    racket_id: str,
    racket_data: ClientRacketUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing racket.

    - **racket_id**: Racket UUID
    - Updates only provided fields
    """
    result = await db.execute(
        select(ClientRacket).where(ClientRacket.id == racket_id)
    )
    racket = result.scalar_one_or_none()

    if not racket:
        raise NotFoundException(f"Racket with ID {racket_id} not found")

    # Update fields
    update_data = racket_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(racket, field, value)

    await db.commit()
    await db.refresh(racket)

    return racket


@router.delete("/{racket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_racket(
    racket_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Mark racket as inactive (client no longer owns it).

    - **racket_id**: Racket UUID
    """
    result = await db.execute(
        select(ClientRacket).where(ClientRacket.id == racket_id)
    )
    racket = result.scalar_one_or_none()

    if not racket:
        raise NotFoundException(f"Racket with ID {racket_id} not found")

    racket.is_active = False
    await db.commit()

    return None


@router.get("/{racket_id}/history", response_model=List[dict])
async def get_racket_history(
    racket_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get full maintenance history for a racket.

    Returns all maintenance records for this racket in chronological order.

    - **racket_id**: Racket UUID
    """
    # First verify racket exists
    racket_result = await db.execute(
        select(ClientRacket).where(ClientRacket.id == racket_id)
    )
    if not racket_result.scalar_one_or_none():
        raise NotFoundException(f"Racket with ID {racket_id} not found")

    # Import here to avoid circular imports
    from app.models.maintenance_record import MaintenanceRecord

    # Get all maintenance records for this racket
    query = select(MaintenanceRecord).where(
        MaintenanceRecord.client_racket_id == racket_id
    ).order_by(MaintenanceRecord.service_date.desc())

    result = await db.execute(query)
    maintenance_records = result.scalars().all()

    return [
        {
            "id": str(record.id),
            "service_date": record.service_date.isoformat(),
            "service_type": record.service_type.value,
            "service_cost": float(record.service_cost) if record.service_cost else None,
            "notes": record.notes
        }
        for record in maintenance_records
    ]
