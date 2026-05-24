from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from asgi_csrf import asgi_csrf
from pathlib import Path
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import engine, Base, AsyncSessionLocal, get_db
import app.models
from app.models.board import Board
from app.config import settings
from app.routers import auth, boards, threads, posts
from app.dependencies import get_current_user
from app.services.seeder import initialize_database
from fastapi.staticfiles import StaticFiles

from fastapi import HTTPException
from app.models.thread import Thread
from app.models.post import Post

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Run seeder
    async with AsyncSessionLocal() as db:
        await initialize_database(db)

    yield


BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"

app = FastAPI(title="sakinfan.com", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie=settings.SESSION_COOKIE_NAME,
    max_age=settings.SESSION_TTL_SECONDS,
)
app.add_middleware(asgi_csrf, signing_secret=settings.SECRET_KEY)

app.include_router(auth.router)
app.include_router(boards.router)
app.include_router(threads.router)
app.include_router(posts.router)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.get("/")
async def index(
    request: Request, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)
):
    query = (
        select(
            Board,
            func.count(Thread.id.distinct()).label("thread_count"),
            func.count(Post.id).label("post_count"),
        )
        .outerjoin(Thread, Board.id == Thread.board_id)
        .outerjoin(Post, Thread.id == Post.thread_id)
        .group_by(Board.id)
        .order_by(Board.display_order)
    )
    
    result = await db.execute(query)
    
    # Map results to a list of dicts for the template
    boards_data = []
    for board, t_count, p_count in result.all():
        boards_data.append({
            "id": board.id,
            "name": board.name,
            "description": board.description,
            "thread_count": t_count,
            "post_count": p_count
        })

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"boards": boards_data, "user": user},
    )

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    async with AsyncSessionLocal() as db:
        user = await get_current_user(request, db)
    return templates.TemplateResponse(
        request=request, name="error/404.html", context={"message": exc.detail, "user": user}, status_code=404
    )

@app.exception_handler(403)
async def forbidden_handler(request: Request, exc: HTTPException):
    async with AsyncSessionLocal() as db:
        user = await get_current_user(request, db)
    return templates.TemplateResponse(
        request=request, name="error/403.html", context={"message": exc.detail, "user": user}, status_code=403
    )

@app.exception_handler(500)
async def server_error_handler(request: Request, exc: Exception):
    return templates.TemplateResponse(
        request=request, name="error/500.html", context={"user": None}, status_code=500
    )