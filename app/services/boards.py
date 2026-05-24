from sqlalchemy.ext.asyncio import AsyncSession
from app.models.board import Board

async def get_board(db: AsyncSession, board_id: int) -> Board | None:
    return await db.get(Board, board_id)