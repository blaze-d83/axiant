from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
import hashlib
from pydantic import BaseModel, field_validator
from fastapi import APIRouter, Depends
from config.settings import settings
from config.db import get_session
from models.token import Token

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    userId: str

    @field_validator("userId")
    @classmethod
    def not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("userId must not be empty")
        return v


class LoginResponse(BaseModel):
    token: str


def _make_token(user_id: str) -> str:
    """Deterministic token: sha-256(salt + userId), prefixed with tok_."""
    raw = f"{settings.token_salt}:{user_id}"
    return "tok_" + hashlib.sha256(raw.encode()).hexdigest()[:32]


@router.post("/mock-login", response_model=LoginResponse)
async def mock_login(
    body: LoginRequest,
    session: AsyncSession = Depends(get_session),
) -> LoginResponse:
    token_value = _make_token(body.userId)

    existing = await session.exec(select(Token).where(Token.token == token_value))
    if not existing.first():
        session.add(Token(token=token_value, user_id=body.userId))

    return LoginResponse(token=token_value)
