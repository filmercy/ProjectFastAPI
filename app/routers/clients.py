"""Clients router for managing tennis shop customers."""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.client import Client
from app.models.client_racket import ClientRacket
from app.schemas.client import ClientCreate, ClientUpdate, ClientResponse, ClientWithRacketsCreate, ClientWithRacketsResponse
from app.utils.pagination import PaginatedResponse
from app.utils.exceptions import NotFoundException

router = APIRouter(prefix="/clients", tags=["Clients"])


@router.get("/", response_model=PaginatedResponse[ClientResponse])
async def list_clients(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by name, email, or phone"),
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    List all clients with pagination and search.

    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 20, max: 100)
    - **search**: Search by name, email, or phone
    - **is_active**: Filter by active status
    """
    # Build query
    query = select(Client)

    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.where(
            (Client.first_name.ilike(search_term)) |
            (Client.last_name.ilike(search_term)) |
            (Client.email.ilike(search_term)) |
            (Client.phone_number.ilike(search_term))
        )

    if is_active is not None:
        query = query.where(Client.is_active == is_active)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(Client.last_name, Client.first_name)

    # Execute query
    result = await db.execute(query)
    clients = result.scalars().all()

    return PaginatedResponse.create(
        items=clients,
        total=total,
        page=page,
        limit=limit
    )


@router.post("/with-rackets", response_model=ClientWithRacketsResponse, status_code=status.HTTP_201_CREATED)
async def create_client_with_rackets(
    client_data: ClientWithRacketsCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new client along with their rackets in a single transaction.

    This is useful when onboarding a new client who already owns rackets.

    **Client fields:**
    - **first_name**: Client's first name (required)
    - **last_name**: Client's last name (required)
    - **email**: Email address (optional)
    - **phone_number**: Phone number (required)
    - Additional address and contact details

    **Rackets field (optional):**
    - **rackets**: List of racket objects, each containing:
      - **brand**: Racket brand (required) - e.g., "Wilson", "Babolat"
      - **model**: Racket model (required) - e.g., "Pro Staff 97"
      - **grip_size**: Grip size (required) - e.g., "4 1/4", "4 3/8"
      - **custom_name**: Optional custom name
      - **serial_number**: Optional serial number
      - **purchase_date**: Optional purchase date
      - **weight_unstrung**: Optional weight in grams
      - **product_id**: Optional link to product in inventory
      - **notes**: Any special notes

    **Example request:**
    ```json
    {
      "first_name": "John",
      "last_name": "Doe",
      "phone_number": "555-0123",
      "email": "john@example.com",
      "rackets": [
        {
          "brand": "Wilson",
          "model": "Pro Staff 97",
          "grip_size": "4 1/4",
          "custom_name": "My main racket"
        },
        {
          "brand": "Babolat",
          "model": "Pure Drive",
          "grip_size": "4 3/8"
        }
      ]
    }
    ```
    """
    # Extract client data (without rackets)
    client_dict = client_data.model_dump(exclude={'rackets'})
    new_client = Client(**client_dict)

    db.add(new_client)
    await db.flush()  # Flush to get the client ID without committing

    # Create rackets for the client
    created_rackets = []
    if client_data.rackets:
        for racket_data in client_data.rackets:
            new_racket = ClientRacket(
                client_id=new_client.id,
                **racket_data.model_dump()
            )
            db.add(new_racket)
            created_rackets.append(new_racket)

    # Commit everything in one transaction
    await db.commit()
    await db.refresh(new_client)

    # Refresh all rackets to get their IDs and timestamps
    for racket in created_rackets:
        await db.refresh(racket)

    # Build response
    response_data = {
        **new_client.__dict__,
        "rackets": [
            {
                "id": racket.id,
                "brand": racket.brand,
                "model": racket.model,
                "grip_size": racket.grip_size,
                "custom_name": racket.custom_name,
                "serial_number": racket.serial_number,
                "purchase_date": racket.purchase_date.isoformat() if racket.purchase_date else None,
                "weight_unstrung": float(racket.weight_unstrung) if racket.weight_unstrung else None,
                "product_id": racket.product_id,
                "notes": racket.notes,
                "is_active": racket.is_active,
                "created_at": racket.created_at.isoformat(),
                "updated_at": racket.updated_at.isoformat()
            }
            for racket in created_rackets
        ]
    }

    return response_data


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific client by ID.

    - **client_id**: Client UUID
    """
    result = await db.execute(select(Client).where(Client.id == str(client_id)))
    client = result.scalar_one_or_none()

    if not client:
        raise NotFoundException(f"Client with ID {client_id} not found")

    return client


@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_data: ClientCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new client.

    - **first_name**: Client's first name
    - **last_name**: Client's last name
    - **email**: Email address (optional)
    - **phone_number**: Phone number (required)
    - Additional address and contact details
    """
    new_client = Client(**client_data.model_dump())

    db.add(new_client)
    await db.commit()
    await db.refresh(new_client)

    return new_client


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: UUID,
    client_data: ClientUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing client.

    - **client_id**: Client UUID
    - Updates only provided fields
    """
    result = await db.execute(select(Client).where(Client.id == str(client_id)))
    client = result.scalar_one_or_none()

    if not client:
        raise NotFoundException(f"Client with ID {client_id} not found")

    # Update fields
    update_data = client_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)

    await db.commit()
    await db.refresh(client)

    return client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Soft delete a client (set is_active = False).

    - **client_id**: Client UUID
    """
    result = await db.execute(select(Client).where(Client.id == str(client_id)))
    client = result.scalar_one_or_none()

    if not client:
        raise NotFoundException(f"Client with ID {client_id} not found")

    client.is_active = False
    await db.commit()

    return None
