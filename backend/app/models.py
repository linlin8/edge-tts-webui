from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class History(Base):
    __tablename__ = "history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(String, nullable=False)
    text_preview: Mapped[str] = mapped_column(String(50), nullable=False)
    voice: Mapped[str] = mapped_column(String, nullable=False)
    rate: Mapped[str] = mapped_column(String, nullable=False, default="+0%")
    volume: Mapped[str] = mapped_column(String, nullable=False, default="+0%")
    pitch: Mapped[str] = mapped_column(String, nullable=False, default="+0Hz")
    audio_path: Mapped[str | None] = mapped_column(String, nullable=True)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_history_created_at", "created_at"),
        Index("ix_history_text_preview", "text_preview"),
    )
