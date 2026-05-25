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
                name="Sakin & Müzik",
                description="Sakin şarkıları, albümleri, söz analizleri ve müzikal tartışmalar.",
                display_order=1,
            ),
            Board(
                name="Konserler & Anılar",
                description="Eski konser kayıtları, fotoğraflar ve grupla ilgili kişisel anılarınız.",
                display_order=2,
            ),
            Board(
                name="Genel Sohbet",
                description="Sakin dışındaki müzikler, filmler ve günlük hayat hakkında sohbet alanı.",
                display_order=3,
            ),
            Board(
                name="Site Hakkında",
                description="Forum için öneriler, duyurular ve hata bildirimleri.",
                display_order=4,
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