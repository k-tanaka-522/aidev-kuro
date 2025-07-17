from pydantic import BaseModel
from typing import Optional
from fastapi import Query


class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 20
    
    @classmethod
    def as_query(
        cls,
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(20, ge=1, le=100, description="Items per page")
    ):
        return cls(page=page, page_size=page_size)
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        return self.page_size