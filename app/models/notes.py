from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
import uuid

# ----------------------------------------
# Helpers


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _new_note_id() -> str:
    return f"note_{uuid.uuid4().hex[:12]}"


# ----------------------------------------
# Notes tables


class Note(SQLModel, table=True):
    """Core note row"""

    __tablename__ = "notes"

    id: str = Field(default_factory=_new_note_id, primary_key=True)
    owner: str = Field(index=True, nullable=False)
    title: str = Field(nullable=False, max_length=80)
    body: str = Field(default="", max_length=500)
    created_at: datetime = Field(default_factory=_utcnow, nullable=False)
    updated_at: Optional[datetime] = Field(default=None)


class NoteResponse(SQLModel):
    id: str
    title: str
    body: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")

    model_config = {"populate_by_name": True}

    @classmethod
    def from_note(cls, note: Note) -> "NoteResponse":
        return cls(
            id=note.id,
            title=note.id,
            body=note.body,
            createdAt=note.created_at,
            updatedAt=note.updated_at,
        )
