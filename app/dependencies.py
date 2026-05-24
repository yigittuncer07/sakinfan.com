from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User


async def get_current_user(
    request: Request, db: AsyncSession = Depends(get_db)
) -> User | None:
    user_id = request.session.get("user_id")
    if not user_id:
        return None

    user = await db.get(User, user_id)
    if not user or user.is_banned:
        request.session.clear()
        return None
    return user


async def require_user(user: User = Depends(get_current_user)) -> User:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    return user


# ADDED: Require Admin Dependency
async def require_admin(user: User = Depends(require_user)) -> User:
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required"
        )
    return user
