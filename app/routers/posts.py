import uuid
from fastapi import APIRouter, Request, Depends, Form, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path

from app.database import get_db
from app.dependencies import get_current_user, require_user
from app.services import posts

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))

@router.get("/thread/{thread_id}", response_class=HTMLResponse)
async def view_thread(thread_id: uuid.UUID, request: Request, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    thread = await posts.get_thread_with_posts(db, thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    # Sort posts chronologically and format body
    thread_posts = sorted(thread.posts, key=lambda p: p.created_at)
    for post in thread_posts:
        post.html_body = posts.format_and_sanitize(post.body)
        
    return templates.TemplateResponse(
        request=request, 
        name="thread.html", 
        context={"thread": thread, "posts": thread_posts, "user": user}
    )

@router.post("/thread/{thread_id}/reply")
async def reply_thread_post(
    thread_id: uuid.UUID,
    request: Request,
    body: str = Form(...),
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user)
):
    await posts.add_reply(db, thread_id, user.id, body)
    return RedirectResponse(url=f"/thread/{thread_id}", status_code=status.HTTP_303_SEE_OTHER)