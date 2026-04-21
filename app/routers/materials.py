from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.material import Material
from app.schemas.material import MaterialResponse


router = APIRouter(prefix="/materials", tags=["materials"])


@router.get("/", response_model=list[MaterialResponse])
async def get_materials(
    project_id: int | None = None, db: AsyncSession = Depends(get_db)
):
    query = select(Material)
    if project_id:
        query = query.where(Material.project_id == project_id)
    result = await db.execute(query)
    return result.scalars().all()
