"""Products router for inventory management."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.product import Product
from app.models.product_category import ProductCategory
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.utils.pagination import PaginatedResponse
from app.utils.exceptions import NotFoundException
from app.config import settings

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=PaginatedResponse[ProductResponse])
async def list_products(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by name or brand"),
    category_id: Optional[str] = Query(None, description="Filter by category"),
    is_active: Optional[bool] = Query(None),
    low_stock: bool = Query(False, description="Show only low stock items"),
    db: AsyncSession = Depends(get_db)
):
    """
    List all products with pagination, search, and filters.

    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 20, max: 100)
    - **search**: Search by name or brand
    - **category_id**: Filter by category UUID
    - **is_active**: Filter by active status
    - **low_stock**: Show only items below LOW_STOCK_THRESHOLD
    """
    # Build query
    query = select(Product)

    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.where(
            (Product.name.ilike(search_term)) |
            (Product.brand.ilike(search_term)) |
            (Product.model.ilike(search_term))
        )

    if category_id:
        query = query.where(Product.category_id == category_id)

    if is_active is not None:
        query = query.where(Product.is_active == is_active)

    if low_stock:
        low_stock_threshold = getattr(settings, 'LOW_STOCK_THRESHOLD', 5)
        query = query.where(Product.quantity_in_stock <= low_stock_threshold)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(Product.brand, Product.name)

    # Execute query
    result = await db.execute(query)
    products = result.scalars().all()

    return PaginatedResponse.create(
        items=products,
        total=total,
        page=page,
        limit=limit
    )


@router.get("/low-stock", response_model=List[ProductResponse])
async def get_low_stock_products(
    db: AsyncSession = Depends(get_db)
):
    """
    Get products with low stock levels.

    Returns products where quantity_in_stock <= LOW_STOCK_THRESHOLD
    """
    low_stock_threshold = getattr(settings, 'LOW_STOCK_THRESHOLD', 5)

    query = select(Product).where(
        (Product.quantity_in_stock <= low_stock_threshold) &
        (Product.is_active == True)
    ).order_by(Product.quantity_in_stock)

    result = await db.execute(query)
    products = result.scalars().all()

    return products


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific product by ID.

    - **product_id**: Product UUID
    """
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise NotFoundException(f"Product with ID {product_id} not found")

    return product


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new product.

    - **category_id**: Category UUID (required)
    - **name**: Product name (required)
    - **brand**: Brand name (required)
    - **model**: Model name (optional)
    - **price**: Retail price (optional)
    - **cost_price**: Cost price for profit tracking (optional)
    - **quantity_in_stock**: Initial stock quantity (default: 0)
    - **specifications**: JSONB field for product-specific attributes
    """
    # Verify category exists
    category_result = await db.execute(
        select(ProductCategory).where(ProductCategory.id == product_data.category_id)
    )
    if not category_result.scalar_one_or_none():
        raise NotFoundException(f"Category with ID {product_data.category_id} not found")

    new_product = Product(**product_data.model_dump())

    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)

    return new_product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing product.

    - **product_id**: Product UUID
    - Updates only provided fields
    """
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise NotFoundException(f"Product with ID {product_id} not found")

    # Update fields
    update_data = product_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(product)

    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Soft delete a product (set is_active = False).

    - **product_id**: Product UUID
    """
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise NotFoundException(f"Product with ID {product_id} not found")

    product.is_active = False
    await db.commit()

    return None
