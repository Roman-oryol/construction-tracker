from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.project import Project


class Material(Base):
    __tablename__ = "materials"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    unit: Mapped[str] = mapped_column(String(20))
    low_stock_threshold: Mapped[float] = mapped_column(server_default="0")
    description: Mapped[str | None] = mapped_column(Text)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    project: Mapped["Project"] = relationship(back_populates="materials")
