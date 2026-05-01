from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.database import get_db
from app.models.consumption import Consumption
from app.models.user import User
from app.models.project_member import ProjectRole
from app.schemas.consumption import ConsumptionCreate, ConsumptionResponse
from app.core.dependencies import get_current_user
from app.routers.materials import _get_material
from app.routers.projects import _get_member_role

router = APIRouter(prefix="/consumptions", tags=["consumptions"])


@router.get("/", response_model=list[ConsumptionResponse])
async def get_consumptions(
    material_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    material = await _get_material(material_id, db)
    await _get_member_role(material.project_id, current_user.id, db)

    result = await db.execute(
        select(Consumption).where(Consumption.material_id == material_id)
    )
    return result.scalars().all()


@router.post(
    "/", response_model=ConsumptionResponse, status_code=status.HTTP_201_CREATED
)
async def create_consumption(
    data: ConsumptionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    material = await _get_material(data.material_id, db)
    role = await _get_member_role(material.project_id, current_user.id, db)

    if role == ProjectRole.viewer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Read-only access"
        )

    consumed_at = data.consumed_at or datetime.now(timezone.utc)

    consumption = Consumption(
        material_id=data.material_id,
        quantity=data.quantity,
        consumed_at=consumed_at,
        brigade=data.brigade,
        comment=data.comment,
    )

    db.add(consumption)
    await db.commit()
    await db.refresh(consumption)
    return consumption


@router.delete("/{consumption_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_consumption(
    consumption_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Consumption).where(Consumption.id == consumption_id)
    )
    consumption = result.scalar_one_or_none()
    if not consumption:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Consumption not found"
        )

    material = await _get_material(consumption.material_id, db)
    role = await _get_member_role(material.project_id, current_user.id, db)
    if role == ProjectRole.viewer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Read-only access"
        )

    await db.delete(consumption)
    await db.commit()
