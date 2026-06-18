import uuid
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.service import AuditService
from app.core.exceptions import ConflictException, NotFoundException
from app.models.customer import Customer
from app.models.user import User
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = CustomerRepository(db)
        self.audit = AuditService(db)

    async def create(self, data: CustomerCreate, current_user: User) -> Customer:
        if await self.repo.get_by_email(data.email):
            raise ConflictException(f"Customer with email '{data.email}' already exists")

        customer = await self.repo.create(data.model_dump())

        await self.audit.log(
            action="CUSTOMER_CREATE",
            resource="customers",
            resource_id=str(customer.id),
            user_id=current_user.id,
            new_values=data.model_dump(mode="json"),
        )
        return customer

    async def get_by_id(self, customer_id: uuid.UUID) -> Customer:
        customer = await self.repo.get_by_id(customer_id)
        if not customer:
            raise NotFoundException("Customer", customer_id)
        return customer

    async def list(
        self,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Customer], int]:
        return await self.repo.search(
            search=search,
            offset=(page - 1) * page_size,
            limit=page_size,
        )

    async def update(
        self, customer_id: uuid.UUID, data: CustomerUpdate, current_user: User
    ) -> Customer:
        customer = await self.get_by_id(customer_id)

        if data.email and data.email != customer.email:
            existing = await self.repo.get_by_email(data.email)
            if existing:
                raise ConflictException(f"Email '{data.email}' is already in use")

        old_values = {"full_name": customer.full_name, "email": customer.email}
        updated = await self.repo.update(customer, data.model_dump(exclude_none=True))

        await self.audit.log(
            action="CUSTOMER_UPDATE",
            resource="customers",
            resource_id=str(customer_id),
            user_id=current_user.id,
            old_values=old_values,
            new_values=data.model_dump(exclude_none=True, mode="json"),
        )
        return updated

    async def delete(self, customer_id: uuid.UUID, current_user: User) -> None:
        customer = await self.get_by_id(customer_id)
        await self.repo.soft_delete(customer)
        await self.audit.log(
            action="CUSTOMER_DELETE",
            resource="customers",
            resource_id=str(customer_id),
            user_id=current_user.id,
            old_values={"email": customer.email},
        )
