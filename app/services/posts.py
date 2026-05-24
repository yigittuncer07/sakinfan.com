import uuid
import markdown
import bleach
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy import func
from sqlalchemy.orm import selectinload

from app.models.thread import Thread
from app.models.post import Post

ALLOWED_TAGS = [
    "p",
    "br",
    "strong",
    "em",
    "u",
    "h1",
    "h2",
    "h3",
    "ul",
    "ol",
    "li",
    "a",
    "blockquote",
    "code",
    "pre",
]


def format_and_sanitize(text: str) -> str:
    html = markdown.markdown(text)
    return bleach.clean(html, tags=ALLOWED_TAGS, strip=True)


async def get_thread(db: AsyncSession, thread_id: uuid.UUID) -> Thread | None:
    result = await db.execute(
        select(Thread)
        .options(selectinload(Thread.author))
        .where(Thread.id == thread_id)
    )
    return result.scalars().first()


async def get_posts_for_thread(
    db: AsyncSession, thread_id: uuid.UUID, page: int = 1, per_page: int = 25
):
    offset = (page - 1) * per_page

    count_result = await db.execute(
        select(func.count(Post.id)).where(Post.thread_id == thread_id)
    )
    total_posts = count_result.scalar() or 0

    result = await db.execute(
        select(Post)
        .options(selectinload(Post.author))
        .where(Post.thread_id == thread_id)
        .order_by(Post.created_at.asc())
        .limit(per_page)
        .offset(offset)
    )
    return result.scalars().all(), total_posts


async def add_reply(
    db: AsyncSession, thread_id: uuid.UUID, author_id: uuid.UUID, body: str
) -> Post:
    post = Post(thread_id=thread_id, author_id=author_id, body=body)
    db.add(post)
    await db.commit()
    return post


async def get_post(db: AsyncSession, post_id: uuid.UUID) -> Post | None:
    return await db.get(Post, post_id)


async def delete_post(db: AsyncSession, post: Post):
    await db.delete(post)
    await db.commit()
