import uuid
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import DeclarativeBase

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_by_id(self, id: uuid.UUID) -> Optional[ModelType]:
        result = await self.db.execute(
            select(self.model).where(
                self.model.id == id,
                self.model.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        offset: int = 0,
        limit: int = 20,
        filters: Optional[List] = None,
    ) -> tuple[List[ModelType], int]:
        base_filter = [self.model.deleted_at.is_(None)]
        if filters:
            base_filter.extend(filters)

        count_query = select(func.count()).select_from(self.model).where(*base_filter)
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()

        query = (
            select(self.model)
            .where(*base_filter)
            .offset(offset)
            .limit(limit)
            .order_by(self.model.created_at.desc())
        )
        result = await self.db.execute(query)
        return result.scalars().all(), total

    async def create(self, data: Dict[str, Any]) -> ModelType:
        instance = self.model(**data)
        self.db.add(instance)
        await self.db.flush()
        await self.db.refresh(instance)
        return instance

    async def update(self, instance: ModelType, data: Dict[str, Any]) -> ModelType:
        for key, value in data.items():
            setattr(instance, key, value)
        await self.db.flush()
        await self.db.refresh(instance)
        return instance

    async def soft_delete(self, instance: ModelType) -> ModelType:
        from datetime import datetime, timezone
        instance.deleted_at = datetime.now(timezone.utc)
        await self.db.flush()
        return instance

    async def hard_delete(self, instance: ModelType) -> None:
        await self.db.delete(instance)
        await self.db.flush()
