"""Pagination utilities."""
from typing import Generic, List, TypeVar
from pydantic import BaseModel
from app.config import settings

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""

    page: int = 1
    limit: int = settings.DEFAULT_PAGE_SIZE

    def get_offset(self) -> int:
        """Calculate the offset for database queries."""
        return (self.page - 1) * self.limit

    def validate_limit(self) -> int:
        """Ensure limit doesn't exceed max page size."""
        if self.limit > settings.MAX_PAGE_SIZE:
            return settings.MAX_PAGE_SIZE
        return self.limit


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""

    items: List[T]
    total: int
    page: int
    limit: int
    total_pages: int

    @classmethod
    def create(cls, items: List[T], total: int, page: int, limit: int):
        """Create a paginated response."""
        total_pages = (total + limit - 1) // limit  # Ceiling division
        return cls(
            items=items,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )
