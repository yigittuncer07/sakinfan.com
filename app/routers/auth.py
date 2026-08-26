import httpx
from fastapi import APIRouter, Request, Depends, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pathlib import Path

from app.database import get_db
from app.models.user import User
from app.services.auth import get_password_hash, verify_password
from app.config import settings

router = APIRouter()
templates = Jinja2Templates(
    directory=str(Path(__file__).resolve().parent.parent / "templates")
)

async def verify_captcha(token: str) -> bool:
    if not token:
        return False
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={"secret": settings.TURNSTILE_SECRET_KEY, "response": token},
        )
        return response.json().get("success", False)

@router.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="auth/login.html", 
        context={"site_key": settings.TURNSTILE_SITE_KEY}
    )

@router.post("/login")
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    cf_turnstile_response: str = Form(alias="cf-turnstile-response", default=""),
    db: AsyncSession = Depends(get_db),
):
    if not await verify_captcha(cf_turnstile_response):
        return templates.TemplateResponse(
            request=request, name="auth/login.html", 
            context={"error": "CAPTCHA doğrulanamadı.", "site_key": settings.TURNSTILE_SITE_KEY}
        )

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()

    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            request=request, name="auth/login.html", 
            context={"error": "Geçersiz kimlik bilgileri.", "site_key": settings.TURNSTILE_SITE_KEY}
        )

    request.session["user_id"] = str(user.id)
    request.session["username"] = user.username
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/register", response_class=HTMLResponse)
async def register_get(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="auth/register.html", 
        context={"site_key": settings.TURNSTILE_SITE_KEY}
    )

@router.post("/register")
async def register_post(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    cf_turnstile_response: str = Form(alias="cf-turnstile-response", default=""),
    db: AsyncSession = Depends(get_db),
):
    if not await verify_captcha(cf_turnstile_response):
        return templates.TemplateResponse(
            request=request, name="auth/register.html", 
            context={"error": "CAPTCHA doğrulanamadı.", "site_key": settings.TURNSTILE_SITE_KEY}
        )

    result = await db.execute(
        select(User).where((User.username == username) | (User.email == email))
    )
    if result.scalars().first():
        return templates.TemplateResponse(
            request=request, name="auth/register.html", 
            context={"error": "Kullanıcı adı veya e-posta zaten kullanımda.", "site_key": settings.TURNSTILE_SITE_KEY}
        )

    new_user = User(
        username=username, email=email, password_hash=get_password_hash(password)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    request.session["user_id"] = str(new_user.id)
    request.session["username"] = new_user.username
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)