"""Product categories router for organizing inventory."""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.product_category import ProductCategory
from app.schemas.product_category import (
    ProductCategoryCreate,
    ProductCategoryUpdate,
    ProductCategoryResponse
)
from app.utils.exceptions import NotFoundException, ConflictException

router = APIRouter(prefix="/categories", tags=["Product Categories"])


@router.get("/", response_model=List[ProductCategoryResponse])
async def list_categories(
    db: AsyncSession = Depends(get_db)
):
    """
    List all product categories.

    Categories are used to organize products:
    - Racquets
    - Strings
    - Grips
    - Overgrips
    - Dampeners
    - Bags
    """
    query = select(ProductCategory).where(ProductCategory.is_active == True).order_by(
        ProductCategory.sort_order,
        ProductCategory.name
    )

    result = await db.execute(query)
    categories = result.scalars().all()

    return categories


@router.get("/{category_id}", response_model=ProductCategoryResponse)
async def get_category(
    category_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific category by ID.

    - **category_id**: Category UUID
    """
    result = await db.execute(
        select(ProductCategory).where(ProductCategory.id == category_id)
    )
    category = result.scalar_one_or_none()

    if not category:
        raise NotFoundException(f"Category with ID {category_id} not found")

    return category


@router.post("/", response_model=ProductCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: ProductCategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new product category.

    - **name**: Category name (e.g., "Strings", "Grips")
    - **slug**: URL-friendly slug (e.g., "strings", "grips")
    - **description**: Optional description
    - **sort_order**: Display order (default: 0)
    """
    # Check if name or slug already exists
    existing = await db.execute(
        select(ProductCategory).where(
            (ProductCategory.name == category_data.name) |
            (ProductCategory.slug == category_data.slug)
        )
    )
    if existing.scalar_one_or_none():
        raise ConflictException("Category with this name or slug already exists")

    new_category = ProductCategory(**category_data.model_dump())

    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)

    return new_category


@router.put("/{category_id}", response_model=ProductCategoryResponse)
async def update_category(
    category_id: str,
    category_data: ProductCategoryUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing category.

    - **category_id**: Category UUID
    - Updates only provided fields
    """
    result = await db.execute(
        select(ProductCategory).where(ProductCategory.id == category_id)
    )
    category = result.scalar_one_or_none()

    if not category:
        raise NotFoundException(f"Category with ID {category_id} not found")

    # Update fields
    update_data = category_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)

    await db.commit()
    await db.refresh(category)

    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Soft delete a category (set is_active = False).

    - **category_id**: Category UUID
    """
    result = await db.execute(
        select(ProductCategory).where(ProductCategory.id == category_id)
    )
    category = result.scalar_one_or_none()

    if not category:
        raise NotFoundException(f"Category with ID {category_id} not found")

    category.is_active = False
    await db.commit()

    return None
