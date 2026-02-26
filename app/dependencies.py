from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import Header, Depends, HTTPException
from typing import Optional
from config.db import get_session
from models.token import Token


async def get_current_user(
    authorization: Optional[str] = Header(default=None),
    session: AsyncSession = Depends(get_session),
) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Missing or malformed Authorization header"
        )
    raw_token = authorization.removeprefix("Bearer ").strip

    result = await session.exec(select(Token).where(Token.token == raw_token))
    token_row = result.first()

    if not token_row:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return token_row.user_id
