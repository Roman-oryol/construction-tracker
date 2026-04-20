from sqlalchemy import func, TIMESTAMP, String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.database import Base


class Material(Base):
    __tablename__ = "materials"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    unit: Mapped[str] = mapped_column(String(20))
    low_stock_threshold: Mapped[float] = mapped_column(default=0)
    description: Mapped[str | None] = mapped_column(Text, default=None)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
