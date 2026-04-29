from __future__ import annotations
import enum
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.user import User


class ProjectRole(str, enum.Enum):
    owner = "owner"
    editor = "editor"
    viewer = "viewer"


class ProjectMember(Base):
    __tablename__ = "project_members"
    __table_args__ = (UniqueConstraint("project_id", "user_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE")
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    role: Mapped[ProjectRole] = mapped_column(
        Enum(ProjectRole), default=ProjectRole.viewer
    )

    project: Mapped["Project"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="memberships")
