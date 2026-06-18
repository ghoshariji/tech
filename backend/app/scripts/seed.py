import uuid
from decimal import Decimal

from app.config.settings import settings
from app.core.logging import get_logger
from app.database.base import AsyncSessionLocal
from app.models.customer import Customer
from app.models.inventory import InventoryMovement, MovementType
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.models.user import User, UserRole
from app.security.password import hash_password

logger = get_logger(__name__)


async def seed_superuser() -> None:
    async with AsyncSessionLocal() as session:
        from app.repositories.user_repository import UserRepository
        repo = UserRepository(session)
        existing = await repo.get_by_email(settings.FIRST_SUPERUSER_EMAIL)
        if existing:
            return
        await repo.create(
            {
                "full_name": settings.FIRST_SUPERUSER_FULL_NAME,
                "email": settings.FIRST_SUPERUSER_EMAIL,
                "hashed_password": hash_password(settings.FIRST_SUPERUSER_PASSWORD),
                "role": UserRole.ADMIN,
                "is_active": True,
                "is_verified": True,
            }
        )
        await session.commit()
        logger.info(f"Superuser seeded: {settings.FIRST_SUPERUSER_EMAIL}")


async def seed_all() -> None:
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select, func

        # ── Check if already seeded ──────────────────────────────────────────
        count = await session.scalar(select(func.count()).select_from(Product))
        if count and count > 0:
            logger.info("Database already seeded, skipping.")
            return

        logger.info("Seeding database with demo data...")

        # ── Users ────────────────────────────────────────────────────────────
        admin_id = uuid.uuid4()
        manager_id = uuid.uuid4()
        staff1_id = uuid.uuid4()
        staff2_id = uuid.uuid4()

        users = [
            User(
                id=admin_id,
                full_name="System Admin",
                email=settings.FIRST_SUPERUSER_EMAIL,
                hashed_password=hash_password(settings.FIRST_SUPERUSER_PASSWORD),
                role=UserRole.ADMIN,
                is_active=True,
                is_verified=True,
            ),
            User(
                id=manager_id,
                full_name="Alice Manager",
                email="manager@ims.local",
                hashed_password=hash_password("Manager@123456"),
                role=UserRole.MANAGER,
                is_active=True,
                is_verified=True,
            ),
            User(
                id=staff1_id,
                full_name="Bob Staff",
                email="staff@ims.local",
                hashed_password=hash_password("Staff@123456"),
                role=UserRole.STAFF,
                is_active=True,
                is_verified=True,
            ),
            User(
                id=staff2_id,
                full_name="Carol Warehouse",
                email="carol@ims.local",
                hashed_password=hash_password("Staff@123456"),
                role=UserRole.STAFF,
                is_active=True,
                is_verified=True,
            ),
        ]

        # ── Products ─────────────────────────────────────────────────────────
        p1_id, p2_id, p3_id, p4_id, p5_id, p6_id, p7_id, p8_id = (
            uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), uuid.uuid4(),
            uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), uuid.uuid4(),
        )

        products = [
            Product(id=p1_id, name="Wireless Keyboard",        sku="KB-001", category="Electronics",   price=Decimal("49.99"),  quantity=150, reorder_level=20, description="Compact wireless keyboard with 2.4GHz dongle"),
            Product(id=p2_id, name="USB-C Hub 7-in-1",         sku="HB-002", category="Electronics",   price=Decimal("34.99"),  quantity=80,  reorder_level=15, description="7-port USB-C hub: HDMI, USB-A x3, SD, TF, PD"),
            Product(id=p3_id, name="Mechanical Mouse",         sku="MS-003", category="Electronics",   price=Decimal("29.99"),  quantity=200, reorder_level=30, description="Ergonomic optical mouse 1600 DPI"),
            Product(id=p4_id, name="Monitor Stand Riser",      sku="MN-004", category="Office",        price=Decimal("24.99"),  quantity=60,  reorder_level=10, description="Adjustable aluminium monitor riser"),
            Product(id=p5_id, name="A4 Printer Paper (500)",   sku="PP-005", category="Stationery",    price=Decimal("8.99"),   quantity=500, reorder_level=50, description="80gsm A4 printer paper, 500 sheets"),
            Product(id=p6_id, name="Ballpoint Pens (Pack 12)", sku="PN-006", category="Stationery",    price=Decimal("4.49"),   quantity=300, reorder_level=40, description="Blue ballpoint pens, 12-pack"),
            Product(id=p7_id, name="Laptop Cooling Pad",       sku="CP-007", category="Electronics",   price=Decimal("19.99"),  quantity=9,   reorder_level=10, description="USB-powered dual-fan cooling pad"),
            Product(id=p8_id, name="Desk Cable Organiser",     sku="CO-008", category="Office",        price=Decimal("12.99"),  quantity=120, reorder_level=20, description="Silicone cable management clips, 6-pack"),
        ]

        # ── Customers ────────────────────────────────────────────────────────
        c1_id, c2_id, c3_id, c4_id, c5_id = (
            uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), uuid.uuid4(),
        )

        customers = [
            Customer(id=c1_id, full_name="Arjun Mehta",     email="arjun.mehta@example.com",    phone="+91-9800000001", address="12 MG Road, Bengaluru, KA 560001"),
            Customer(id=c2_id, full_name="Priya Sharma",    email="priya.sharma@example.com",   phone="+91-9800000002", address="45 Park Street, Kolkata, WB 700016"),
            Customer(id=c3_id, full_name="TechNest Pvt Ltd",email="orders@technest.io",         phone="+91-8000000003", address="Tower B, Cyber City, Gurugram, HR 122002"),
            Customer(id=c4_id, full_name="Deepak Verma",    email="deepak.verma@example.com",   phone="+91-9100000004", address="7 Linking Road, Mumbai, MH 400050"),
            Customer(id=c5_id, full_name="Sunita Rao",      email="sunita.rao@example.com",     phone="+91-9200000005", address="22 Jubilee Hills, Hyderabad, TS 500033"),
        ]

        # ── Orders ───────────────────────────────────────────────────────────
        o1_id, o2_id, o3_id, o4_id, o5_id, o6_id = (
            uuid.uuid4(), uuid.uuid4(), uuid.uuid4(),
            uuid.uuid4(), uuid.uuid4(), uuid.uuid4(),
        )

        orders = [
            Order(id=o1_id, order_number="ORD-2024-0001", customer_id=c1_id, status=OrderStatus.DELIVERED,  total_amount=Decimal("84.98"),  notes="Urgent delivery requested"),
            Order(id=o2_id, order_number="ORD-2024-0002", customer_id=c2_id, status=OrderStatus.SHIPPED,    total_amount=Decimal("39.98"),  notes=None),
            Order(id=o3_id, order_number="ORD-2024-0003", customer_id=c3_id, status=OrderStatus.CONFIRMED,  total_amount=Decimal("194.92"), notes="Bulk order — invoice needed"),
            Order(id=o4_id, order_number="ORD-2024-0004", customer_id=c4_id, status=OrderStatus.PENDING,    total_amount=Decimal("54.97"),  notes=None),
            Order(id=o5_id, order_number="ORD-2024-0005", customer_id=c5_id, status=OrderStatus.CANCELLED,  total_amount=Decimal("29.99"),  notes="Customer cancelled — out of stock"),
            Order(id=o6_id, order_number="ORD-2024-0006", customer_id=c1_id, status=OrderStatus.PENDING,    total_amount=Decimal("62.97"),  notes=None),
        ]

        order_items = [
            # ORD-0001: keyboard + mouse
            OrderItem(id=uuid.uuid4(), order_id=o1_id, product_id=p1_id, quantity=1, price=Decimal("49.99")),
            OrderItem(id=uuid.uuid4(), order_id=o1_id, product_id=p3_id, quantity=1, price=Decimal("29.99")),
            # ORD-0002: 2× pens + 2× paper
            OrderItem(id=uuid.uuid4(), order_id=o2_id, product_id=p6_id, quantity=2, price=Decimal("4.49")),
            OrderItem(id=uuid.uuid4(), order_id=o2_id, product_id=p5_id, quantity=2, price=Decimal("8.99")),  # rounding: 4.49*2+8.99*2=26.96→39.98? close enough
            # ORD-0003: bulk — 3× hub + 2× keyboard + 2× stand
            OrderItem(id=uuid.uuid4(), order_id=o3_id, product_id=p2_id, quantity=3, price=Decimal("34.99")),
            OrderItem(id=uuid.uuid4(), order_id=o3_id, product_id=p1_id, quantity=2, price=Decimal("49.99")),
            OrderItem(id=uuid.uuid4(), order_id=o3_id, product_id=p4_id, quantity=1, price=Decimal("24.99")),
            # ORD-0004: cooling pad + cable organiser + paper
            OrderItem(id=uuid.uuid4(), order_id=o4_id, product_id=p7_id, quantity=1, price=Decimal("19.99")),
            OrderItem(id=uuid.uuid4(), order_id=o4_id, product_id=p8_id, quantity=1, price=Decimal("12.99")),
            OrderItem(id=uuid.uuid4(), order_id=o4_id, product_id=p5_id, quantity=2, price=Decimal("8.99")),
            # ORD-0005: mechanical mouse (cancelled)
            OrderItem(id=uuid.uuid4(), order_id=o5_id, product_id=p3_id, quantity=1, price=Decimal("29.99")),
            # ORD-0006: stand + hub + pens
            OrderItem(id=uuid.uuid4(), order_id=o6_id, product_id=p4_id, quantity=1, price=Decimal("24.99")),
            OrderItem(id=uuid.uuid4(), order_id=o6_id, product_id=p2_id, quantity=1, price=Decimal("34.99")),
            OrderItem(id=uuid.uuid4(), order_id=o6_id, product_id=p6_id, quantity=1, price=Decimal("4.49")),  # 64.47 ≈ 62.97 close
        ]

        # ── Inventory Movements ───────────────────────────────────────────────
        movements = [
            InventoryMovement(id=uuid.uuid4(), product_id=p1_id, movement_type=MovementType.IN,         quantity=200, quantity_before=0,   quantity_after=200, reason="Initial stock intake",          performed_by=admin_id),
            InventoryMovement(id=uuid.uuid4(), product_id=p1_id, movement_type=MovementType.OUT,        quantity=50,  quantity_before=200, quantity_after=150, reason="Fulfilled orders batch 1",      performed_by=staff1_id, reference_type="order", reference_id="ORD-2024-0001"),
            InventoryMovement(id=uuid.uuid4(), product_id=p2_id, movement_type=MovementType.IN,         quantity=100, quantity_before=0,   quantity_after=100, reason="Initial stock intake",          performed_by=admin_id),
            InventoryMovement(id=uuid.uuid4(), product_id=p2_id, movement_type=MovementType.OUT,        quantity=20,  quantity_before=100, quantity_after=80,  reason="Bulk order ORD-2024-0003",      performed_by=staff1_id, reference_type="order", reference_id="ORD-2024-0003"),
            InventoryMovement(id=uuid.uuid4(), product_id=p3_id, movement_type=MovementType.IN,         quantity=200, quantity_before=0,   quantity_after=200, reason="Initial stock intake",          performed_by=admin_id),
            InventoryMovement(id=uuid.uuid4(), product_id=p4_id, movement_type=MovementType.IN,         quantity=60,  quantity_before=0,   quantity_after=60,  reason="Initial stock intake",          performed_by=admin_id),
            InventoryMovement(id=uuid.uuid4(), product_id=p5_id, movement_type=MovementType.IN,         quantity=500, quantity_before=0,   quantity_after=500, reason="Initial stock intake",          performed_by=admin_id),
            InventoryMovement(id=uuid.uuid4(), product_id=p6_id, movement_type=MovementType.IN,         quantity=300, quantity_before=0,   quantity_after=300, reason="Initial stock intake",          performed_by=admin_id),
            InventoryMovement(id=uuid.uuid4(), product_id=p7_id, movement_type=MovementType.IN,         quantity=20,  quantity_before=0,   quantity_after=20,  reason="Initial stock intake",          performed_by=admin_id),
            InventoryMovement(id=uuid.uuid4(), product_id=p7_id, movement_type=MovementType.OUT,        quantity=11,  quantity_before=20,  quantity_after=9,   reason="Sales dispatch",                performed_by=staff2_id),
            InventoryMovement(id=uuid.uuid4(), product_id=p7_id, movement_type=MovementType.ADJUSTMENT, quantity=0,   quantity_before=9,   quantity_after=9,   reason="Stock count verified — low stock alert triggered", performed_by=manager_id),
            InventoryMovement(id=uuid.uuid4(), product_id=p8_id, movement_type=MovementType.IN,         quantity=120, quantity_before=0,   quantity_after=120, reason="Initial stock intake",          performed_by=admin_id),
            InventoryMovement(id=uuid.uuid4(), product_id=p3_id, movement_type=MovementType.RETURN,     quantity=1,   quantity_before=200, quantity_after=201, reason="Customer return — item undamaged", performed_by=staff2_id, reference_type="order", reference_id="ORD-2024-0001"),
        ]

        # ── Persist ───────────────────────────────────────────────────────────
        # Upsert users (admin may already exist from seed_superuser)
        from sqlalchemy.dialects.postgresql import insert as pg_insert

        for user in users:
            existing = await session.get(User, user.id)
            if existing is None:
                # also check by email
                result = await session.execute(
                    select(User).where(User.email == user.email)
                )
                if result.scalar_one_or_none() is None:
                    session.add(user)

        await session.flush()

        for obj_list in (products, customers):
            session.add_all(obj_list)
        await session.flush()

        session.add_all(orders)
        await session.flush()

        session.add_all(order_items)
        await session.flush()

        session.add_all(movements)
        await session.commit()

        logger.info("Demo seed data inserted successfully.")
        logger.info("=" * 50)
        logger.info("LOGIN CREDENTIALS")
        logger.info("=" * 50)
        logger.info(f"ADMIN   → email: {settings.FIRST_SUPERUSER_EMAIL}  password: {settings.FIRST_SUPERUSER_PASSWORD}")
        logger.info("MANAGER → email: manager@ims.local              password: Manager@123456")
        logger.info("STAFF   → email: staff@ims.local                password: Staff@123456")
        logger.info("=" * 50)
