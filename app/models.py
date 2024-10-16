from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import JSON, Column
from sqlmodel import SQLModel, Field


class PdfFile(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    langchain: dict = Field(sa_column=Column(JSON))
    file_name: str
    file_path: str
