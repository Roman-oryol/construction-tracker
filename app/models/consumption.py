from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import String, Text, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.material import Material


class Consumption(Base):
    __tablename__ = "consumptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    material_id: Mapped[int] = mapped_column(ForeignKey("materials.id"))
    quantity: Mapped[float] = mapped_column(Numeric(10, 3))
    consumed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    brigade: Mapped[str | None] = mapped_column(String(100))
    comment: Mapped[str | None] = mapped_column(Text)

    material: Mapped["Material"] = relationship(back_populates="consumptions")
