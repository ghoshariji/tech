from typing import Optional
from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    search: Optional[str] = Field(default=None, max_length=200)
    sort_by: Optional[str] = Field(default=None, max_length=50)
    sort_order: Optional[str] = Field(default="asc", pattern="^(asc|desc)$")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
