from sqlmodel import select, desc
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Optional, List
from pydantic import BaseModel, field_validator, model_validator
from fastapi import APIRouter, HTTPException, Depends, Response
from models.notes import Note, NoteResponse
from config.db import get_session
from dependencies import get_current_user
from datetime import datetime, timezone

router = APIRouter(prefix="/notes", tags=["notes"])

class CreateNoteRequest(BaseModel):
    title: str
    body: Optional[str] = ""

    @field_validator("title")
    @classmethod
    def title_is_valid(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Title is required")
        if len(v) > 80:
            raise ValueError("Title must be less than 80 characters")
        return v

    @field_validator("body")
    @classmethod
    def body_is_valid(cls, v: str) -> str:
        v = v.strip()
        if v is None:
            return ""
        if len(v) > 500:
            raise ValueError("Body should be less than 500 characters")
        return v

class PathNoteRequest(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None

    @model_validator(mode="after")
    def at_least_one(self) -> "PathNoteRequest":
        if self.title is None and self.body is None:
            raise ValueError("Request must contain: title or body")
        return self

    @field_validator("title")
    @classmethod
    def title_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("Title must not be empty")
        if len(v) > 80:
            raise ValueError("Title must not be greater than 80 characters")
        return v

    @field_validator("body")
    @classmethod
    def body_is_valid(cls, v: str) -> str:
        v = v.strip()
        if v is None and len(v) > 500:
            raise ValueError("Body should be less than 500 characters")
        return v

async def _get_note_or_404(note_id: str, session: AsyncSession) -> Note:
    note = await session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

def _assert_owner(note: Note, user_id: str) -> None:
    if note.owner != user_id:
        raise HTTPException(status_code=403, detail="Not the owner")

# ------------------------------------------------------------------------
# Routes

@router.post("", status_code=201, response_model=NoteResponse)
async def create_note(
        body: CreateNoteRequest,
        session: AsyncSession = Depends(get_session),
        user_id: str = Depends(get_current_user),
        ) -> NoteResponse:
    note = Note(owner=user_id, title=body.title, body=body.body or "")
    session.add(note)
    await session.flush()
    await session.refresh(note)
    return NoteResponse.from_note(note)

@router.get("", status_code=200, response_model=List[NoteResponse])
async def list_notes(
        session: AsyncSession = Depends(get_session),
        user_id: str = Depends(get_current_user),
        ) -> List[NoteResponse]:
    result = await session.exec(
            select(Note).where(Note.owner == user_id).order_by(desc(Note.created_at))
            )
    return [NoteResponse.from_note(n) for n in result.all()]


@router.patch("/{note_id}", status_code=200, response_model=NoteResponse)
async def update_note(
        note_id: str,
        body: PathNoteRequest,
        session: AsyncSession = Depends(get_session),
        user_id: str = Depends(get_current_user),
        ) -> NoteResponse:
    note = await _get_note_or_404(note_id, session)
    _assert_owner(note, user_id)

    if body.title is not None:
        note.title = body.title
    if body.body is not None:
        note.body = body.body
        note.updated_at = datetime.now(timezone.utc)

    session.add(note)
    await session.flush()
    await session.refresh(note)
    return NoteResponse.from_note(note)

@router.delete("/{note_id}", status_code=204)
async def delete_note(
        note_id: str,
        session: AsyncSession = Depends(get_session),
        user_id: str = Depends(get_current_user),
        ) -> Response:
    note = await _get_note_or_404(note_id, session)
    _assert_owner(note, user_id)
    await session.delete(note)
    return Response(status_code=204)

