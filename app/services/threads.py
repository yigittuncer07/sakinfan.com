import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.thread import Thread
from app.models.post import Post

async def get_threads_for_board(db: AsyncSession, board_id: int):
    result = await db.execute(
        select(Thread).where(Thread.board_id == board_id).order_by(Thread.created_at.desc())
    )
    return result.scalars().all()

async def create_thread_with_post(db: AsyncSession, board_id: int, author_id: uuid.UUID, title: str, body: str) -> Thread:
    thread = Thread(board_id=board_id, author_id=author_id, title=title)
    db.add(thread)
    await db.flush() # Get thread ID before committing
    
    post = Post(thread_id=thread.id, author_id=author_id, body=body)
    db.add(post)
    await db.commit()
    return thread