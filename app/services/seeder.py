from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.board import Board
from app.models.user import User
from app.services.auth import get_password_hash
from app.config import settings


async def initialize_database(db: AsyncSession):
    board_result = await db.execute(select(Board))
    if not board_result.scalars().first():
        boards = [
            Board(
                name="Site Hakkında",
                description="Kurallar, İletişim, Duyurular",
                display_order=1,
            ),
            Board(
                name="Sakin",
                description="Grup hakkında yorumlar.",
                display_order=2,
            ),
            Board(
                name="HAYAT - 2008",
                description="Albüm hakkında yorumlar",
                display_order=3,
            ),
            Board(
                name="Müzik",
                description="Yerli Müzisyenler, Yabancı Müzisyenler, Amatör Müzik",
                display_order=4,
            ),
            Board(
                name="Kültür - Sanat",
                description="Edebiyat, Felsefe, Sinema & Tiyatro",
                display_order=5,
            ),
            Board(
                name="Genel",
                description="Kategori dışı konular...",
                display_order=6,
            ),
        ]
        db.add_all(boards)

    # 2. Seed default admin user
    user_result = await db.execute(
        select(User).where(User.username == settings.ADMIN_USERNAME)
    )
    if not user_result.scalars().first():
        admin_user = User(
            username=settings.ADMIN_USERNAME,
            email=settings.ADMIN_EMAIL,
            password_hash=get_password_hash(settings.ADMIN_PASSWORD),
            is_admin=True,
        )
        db.add(admin_user)

    # Commit all changes
    await db.commit()