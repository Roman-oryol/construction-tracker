from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.material import Material
from app.models.project_member import ProjectMember, ProjectRole


async def get_material_or_404(material_id: int, db: AsyncSession) -> Material:
    result = await db.execute(select(Material).where(Material.id == material_id))
    material = result.scalar_one_or_none()
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Material not found"
        )
    return material


async def get_member_role(
    project_id: int, user_id: int, db: AsyncSession
) -> ProjectRole:
    result = await db.execute(
        select(ProjectMember.role).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
    )
    role = result.scalar_one_or_none()
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    return role