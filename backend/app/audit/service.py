import uuid
from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.core.logging import get_logger

logger = get_logger(__name__)



class AuditService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(
        self,
        action: str,
        resource: str,
        resource_id: Optional[str] = None,
        user_id: Optional[uuid.UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        status: str = "SUCCESS",
        error_message: Optional[str] = None,
    ) -> AuditLog:
        try:
            entry = AuditLog(
                user_id=user_id,
                action=action,
                resource=resource,
                resource_id=str(resource_id) if resource_id else None,
                ip_address=ip_address,
                user_agent=user_agent,
                old_values=old_values,
                new_values=new_values,
                status=status,
                error_message=error_message,
            )
            self.db.add(entry)
            await self.db.flush()
            logger.bind(
                action=action,
                resource=resource,
                resource_id=resource_id,
                user_id=str(user_id) if user_id else None,
            ).info(f"Audit: {action} on {resource}")
            return entry
        except Exception as exc:
            logger.error(f"Failed to write audit log: {exc}")
            raise
