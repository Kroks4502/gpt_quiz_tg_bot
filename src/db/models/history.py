from sqlalchemy import BigInteger
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from . import Base


class AssistantHistory(Base):
    __tablename__ = "assistant_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, index=True)

    assistant: Mapped[str] = mapped_column(nullable=True)
    model_params: Mapped[dict] = mapped_column(JSONB, nullable=True)
    prompt_params: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    messages: Mapped[list] = mapped_column(JSONB, nullable=True)
    result: Mapped[dict | list | str | None] = mapped_column(JSONB, nullable=True)

    error: Mapped[str] = mapped_column(JSONB, nullable=True)
