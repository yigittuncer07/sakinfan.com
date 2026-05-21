from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from asgi_csrf import asgi_csrf
from pathlib import Path

from app.database import engine, Base
import app.models
from app.config import settings
from app.routers import auth
from app.dependencies import get_current_user

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"

app = FastAPI(title="sakinfan.com", lifespan=lifespan)

# Middlewares
app.add_middleware(
    SessionMiddleware, 
    secret_key=settings.SECRET_KEY,
    session_cookie=settings.SESSION_COOKIE_NAME,
    max_age=settings.SESSION_TTL_SECONDS
)
app.add_middleware(asgi_csrf, signing_secret=settings.SECRET_KEY)

# Routers
app.include_router(auth.router)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@app.get("/")
async def index(request: Request, user=Depends(get_current_user)):
    dummy_boards = [
        {"id": 1, "name": "General Discussion", "description": "Talk about anything."},
        {"id": 2, "name": "Tech & Code", "description": "Programming and hardware."}
    ]
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={"boards": dummy_boards, "user": user}
    )