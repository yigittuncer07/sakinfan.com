from fastapi import APIRouter, Request, Depends, Form, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path

from app.database import get_db
from app.services import boards, threads

import uuid
from app.dependencies import require_user, require_admin

router = APIRouter()
templates = Jinja2Templates(
    directory=str(Path(__file__).resolve().parent.parent / "templates")
)


@router.get("/board/{board_id}/new", response_class=HTMLResponse)
async def new_thread_get(
    board_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    board = await boards.get_board(db, board_id)
    if not board:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(
        request=request, name="thread_new.html", context={"board": board, "user": user}
    )


@router.post("/board/{board_id}/new")
async def new_thread_post(
    board_id: int,
    request: Request,
    title: str = Form(...),
    body: str = Form(...),
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    thread = await threads.create_thread_with_post(db, board_id, user.id, title, body)
    # Redirects to the thread view (which we will build in step 5)
    return RedirectResponse(
        url=f"/thread/{thread.id}", status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/thread/{thread_id}/delete")
async def delete_thread_action(
    thread_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    thread = await threads.get_thread(db, thread_id)
    if not thread:
        raise HTTPException(status_code=404)

    board_id = thread.board_id
    await threads.delete_thread(db, thread)
    return RedirectResponse(
        url=f"/board/{board_id}", status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/thread/{thread_id}/lock")
async def lock_thread_action(
    thread_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    thread = await threads.get_thread(db, thread_id)
    if thread:
        await threads.toggle_lock(db, thread)
    return RedirectResponse(
        url=f"/thread/{thread_id}", status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/thread/{thread_id}/pin")
async def pin_thread_action(
    thread_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    thread = await threads.get_thread(db, thread_id)
    if thread:
        await threads.toggle_pin(db, thread)
    return RedirectResponse(
        url=f"/thread/{thread_id}", status_code=status.HTTP_303_SEE_OTHER
    )
