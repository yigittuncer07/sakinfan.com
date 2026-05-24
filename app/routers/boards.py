from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path

from app.database import get_db
from app.dependencies import get_current_user
from app.services import boards, threads

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))

@router.get("/board/{board_id}", response_class=HTMLResponse)
async def view_board(board_id: int, request: Request, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    board = await boards.get_board(db, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
        
    board_threads = await threads.get_threads_for_board(db, board_id)
    return templates.TemplateResponse(
        request=request, 
        name="board.html", 
        context={"board": board, "threads": board_threads, "user": user}
    )