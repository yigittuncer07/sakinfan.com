import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from app.models.thread import Thread
from app.models.post import Post


async def get_threads_for_board(
    db: AsyncSession, board_id: int, page: int = 1, per_page: int = 20
):
    offset = (page - 1) * per_page

    count_result = await db.execute(
        select(func.count()).where(Thread.board_id == board_id)
    )
    total_threads = count_result.scalar() or 0

    result = await db.execute(
        select(Thread)
        .where(Thread.board_id == board_id)
        # UPDATED: Sort by pinned first, then chronological
        .order_by(Thread.is_pinned.desc(), Thread.created_at.desc())
        .limit(per_page)
        .offset(offset)
    )
    return result.scalars().all(), total_threads


async def get_thread(db: AsyncSession, thread_id: uuid.UUID) -> Thread | None:
    return await db.get(Thread, thread_id)


async def create_thread_with_post(
    db: AsyncSession, board_id: int, author_id: uuid.UUID, title: str, body: str
) -> Thread:
    thread = Thread(board_id=board_id, author_id=author_id, title=title)
    db.add(thread)
    await db.flush()

    post = Post(thread_id=thread.id, author_id=author_id, body=body)
    db.add(post)
    await db.commit()
    return thread


async def delete_thread(db: AsyncSession, thread: Thread):
    await db.execute(delete(Post).where(Post.thread_id == thread.id))
    await db.delete(thread)
    await db.commit()


async def toggle_lock(db: AsyncSession, thread: Thread):
    thread.is_locked = not thread.is_locked
    await db.commit()


async def toggle_pin(db: AsyncSession, thread: Thread):
    thread.is_pinned = not thread.is_pinned
    await db.commit()
