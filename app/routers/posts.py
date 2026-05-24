import uuid
import math
from fastapi import APIRouter, Request, Depends, Form, status, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path

from app.database import get_db
from app.dependencies import get_current_user, require_user
from app.services import posts

router = APIRouter()
templates = Jinja2Templates(
    directory=str(Path(__file__).resolve().parent.parent / "templates")
)


@router.get("/thread/{thread_id}", response_class=HTMLResponse)
async def view_thread(
    thread_id: uuid.UUID,
    request: Request,
    page: int = Query(1, ge=1),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    thread = await posts.get_thread(db, thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    thread_posts, total_posts = await posts.get_posts_for_thread(
        db, thread_id, page=page
    )
    total_pages = math.ceil(total_posts / 25) if total_posts > 0 else 1

    for post in thread_posts:
        post.html_body = posts.format_and_sanitize(post.body)

    return templates.TemplateResponse(
        request=request,
        name="thread.html",
        context={
            "thread": thread,
            "posts": thread_posts,
            "user": user,
            "current_page": page,
            "total_pages": total_pages,
        },
    )

@router.post("/thread/{thread_id}/reply")
async def reply_thread_post(
    thread_id: uuid.UUID,
    request: Request,
    body: str = Form(...),
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    # Check if thread is locked
    thread = await posts.get_thread(db, thread_id)
    if not thread:
        raise HTTPException(status_code=404)
    if thread.is_locked and not user.is_admin:
        raise HTTPException(status_code=403, detail="Thread is locked")

    await posts.add_reply(db, thread_id, user.id, body)
    return RedirectResponse(
        url=f"/thread/{thread_id}", status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/post/{post_id}/delete")
async def delete_post_action(
    post_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(require_user)
):
    post = await posts.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404)

    if post.author_id != user.id and not user.is_admin:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this post"
        )

    thread_id = post.thread_id
    await posts.delete_post(db, post)
    return RedirectResponse(
        url=f"/thread/{thread_id}", status_code=status.HTTP_303_SEE_OTHER
    )
