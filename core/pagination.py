from typing import Optional

from sqlalchemy.orm import Query

from schemas.base import PaginatedResponse, PaginationMeta


def paginate_query(
    query: Query,
    page: int,
    limit: int,
    skip: Optional[int] = None,
) -> PaginatedResponse:
    total = query.order_by(None).count()
    offset = skip if skip is not None else (page - 1) * limit
    current_page = (offset // limit) + 1
    total_pages = (total + limit - 1) // limit if total else 0
    items = query.offset(offset).limit(limit).all()

    return PaginatedResponse(
        items=items,
        pagination=PaginationMeta(
            page=current_page,
            limit=limit,
            total=total,
            total_pages=total_pages,
            has_next=current_page < total_pages,
            has_previous=current_page > 1,
        ),
    )
