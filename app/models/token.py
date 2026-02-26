from sqlmodel import SQLModel, Field


class Token(SQLModel, table=True):
    """Maps a fake bearer token to user.Id"""

    __tablename__ = "tokens"

    token: str = Field(primary_key=True)
    user_id: str = Field(index=True)
