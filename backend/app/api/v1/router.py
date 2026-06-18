from fastapi import APIRouter
from app.api.v1.endpoints import auth, products, customers, orders, inventory, dashboard, audit, users

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(products.router)
api_router.include_router(customers.router)
api_router.include_router(orders.router)
api_router.include_router(inventory.router)
api_router.include_router(dashboard.router)
api_router.include_router(audit.router)
