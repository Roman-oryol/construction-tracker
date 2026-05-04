from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.database import get_db
from app.models.delivery import Delivery
from app.models.user import User
from app.models.project_member import ProjectRole
from app.schemas.delivery import DeliveryCreate, DeliveryResponse
from app.core.dependencies import get_current_user
from app.core.shortcuts import get_material_or_404, get_member_role

router = APIRouter(prefix="/deliveries", tags=["deliveries"])


@router.get("/", response_model=list[DeliveryResponse])
async def get_deliveries(
    material_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    material = await get_material_or_404(material_id, db)
    await get_member_role(material.project_id, current_user.id, db)

    result = await db.execute(
        select(Delivery).where(Delivery.material_id == material_id)
    )
    return result.scalars().all()


@router.post("/", response_model=DeliveryResponse, status_code=status.HTTP_201_CREATED)
async def create_delivery(
    data: DeliveryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    material = await get_material_or_404(data.material_id, db)
    role = await get_member_role(material.project_id, current_user.id, db)

    if role == ProjectRole.viewer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Read-only access"
        )

    delivered_at = data.delivered_at or datetime.now(timezone.utc)

    delivery = Delivery(
        material_id=data.material_id,
        quantity=data.quantity,
        delivered_at=delivered_at,
        supplier=data.supplier,
        comment=data.comment,
    )
    db.add(delivery)
    await db.commit()
    await db.refresh(delivery)
    return delivery


@router.delete("/{delivery_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_delivery(
    delivery_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Delivery).where(Delivery.id == delivery_id))
    delivery = result.scalar_one_or_none()
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found"
        )

    material = await get_material_or_404(delivery.material_id, db)
    role = await get_member_role(material.project_id, current_user.id, db)

    if role == ProjectRole.viewer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Read-only access"
        )

    await db.delete(delivery)
    await db.commit()
