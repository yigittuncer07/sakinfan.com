import uuid
import markdown
import bleach
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.thread import Thread
from app.models.post import Post

ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'ul', 'ol', 'li', 'a', 'blockquote', 'code', 'pre']

def format_and_sanitize(text: str) -> str:
    html = markdown.markdown(text)
    return bleach.clean(html, tags=ALLOWED_TAGS, strip=True)

async def get_thread_with_posts(db: AsyncSession, thread_id: uuid.UUID) -> Thread | None:
    result = await db.execute(
        select(Thread)
        .options(
            selectinload(Thread.author),
            selectinload(Thread.posts).selectinload(Post.author)
        )
        .where(Thread.id == thread_id)
    )
    return result.scalars().first()

async def add_reply(db: AsyncSession, thread_id: uuid.UUID, author_id: uuid.UUID, body: str) -> Post:
    post = Post(thread_id=thread_id, author_id=author_id, body=body)
    db.add(post)
    await db.commit()
    return post