import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.models.inventory import MovementType


class InventoryAdjustRequest(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(..., description="Positive to add, negative to remove")
    movement_type: MovementType = MovementType.ADJUSTMENT
    reason: Optional[str] = Field(default=None, max_length=500)


class InventoryMovementResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    movement_type: MovementType
    quantity: int
    quantity_before: int
    quantity_after: int
    reference_id: Optional[str] = None
    reference_type: Optional[str] = None
    reason: Optional[str] = None
    performed_by: Optional[uuid.UUID] = None
    created_at: datetime

    model_config = {"from_attributes": True}
