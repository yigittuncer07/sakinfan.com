from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from asgi_csrf import asgi_csrf
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import engine, Base, AsyncSessionLocal, get_db
import app.models
from app.models.board import Board
from app.config import settings
from app.routers import auth, boards, threads, posts
from app.dependencies import get_current_user

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Seed a default board if none exist
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Board))
        if not res.scalars().first():
            db.add(Board(name="General Discussion", description="Talk about anything."))
            await db.commit()
    yield

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"

app = FastAPI(title="sakinfan.com", lifespan=lifespan)

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY, session_cookie=settings.SESSION_COOKIE_NAME, max_age=settings.SESSION_TTL_SECONDS)
app.add_middleware(asgi_csrf, signing_secret=settings.SECRET_KEY)

app.include_router(auth.router)
app.include_router(boards.router)
app.include_router(threads.router)
app.include_router(posts.router)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@app.get("/")
async def index(request: Request, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await db.execute(select(Board).order_by(Board.display_order))
    real_boards = result.scalars().all()
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={"boards": real_boards, "user": user}
    )