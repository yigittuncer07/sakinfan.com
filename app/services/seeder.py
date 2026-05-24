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
                name="General Discussion",
                description="Talk about anything.",
                display_order=1,
            ),
            Board(
                name="Tech & Code",
                description="Programming and hardware.",
                display_order=2,
            ),
            Board(
                name="Site Feedback",
                description="Bug reports and suggestions.",
                display_order=3,
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
