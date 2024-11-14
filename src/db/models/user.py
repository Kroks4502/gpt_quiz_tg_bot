from bot.constants import Mode
from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from . import Base


class User(Base):
    __tablename__ = "user"

    # TG attrs
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(nullable=True)
    last_name: Mapped[str] = mapped_column(nullable=True)
    username: Mapped[str] = mapped_column(nullable=True)
    phone: Mapped[str] = mapped_column(nullable=True)
    lang_code: Mapped[str] = mapped_column(nullable=True)
    usernames: Mapped[str] = mapped_column(nullable=True)

    # Bot attrs
    bot_mode: Mapped[str] = mapped_column(nullable=False, default=Mode.COMPLEX)


class UserTopic(Base):
    __tablename__ = "user_topic"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    topic: Mapped[str]
    subtopics: Mapped[list] = mapped_column(JSONB)
