from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.material import Material
from app.models.delivery import Delivery
from app.models.consumption import Consumption
from app.models.project import Project
from app.models.project_member import ProjectMember, ProjectRole
from app.models.user import User
from app.schemas.material import (
    MaterialCreate,
    MaterialUpdate,
    MaterialResponse,
    StockStatus,
)
from app.core.dependencies import get_current_user
from app.core.shortcuts import get_material_or_404, get_member_role

router = APIRouter(prefix="/materials", tags=["materials"])


async def _calc_stock(material_id: int, db: AsyncSession) -> float:
    deliveries = await db.scalar(
        select(func.coalesce(func.sum(Delivery.quantity), 0)).where(
            Delivery.material_id == material_id
        )
    )
    consumptions = await db.scalar(
        select(func.coalesce(func.sum(Consumption.quantity), 0)).where(
            Consumption.material_id == material_id
        )
    )
    return float(deliveries or 0) - float(consumptions or 0)


def _calc_status(stock: float, threshold: float) -> StockStatus:
    if stock <= 0:
        return StockStatus.critical
    if stock < threshold:
        return StockStatus.low
    return StockStatus.ok


@router.get("/", response_model=list[MaterialResponse])
async def get_materials(
    project_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        select(Material)
        .join(Project)
        .join(ProjectMember)
        .where(ProjectMember.user_id == current_user.id)
    )
    if project_id:
        await get_member_role(
            project_id, current_user.id, db
        )  # проверяем доступ к проекту
        query = query.where(Material.project_id == project_id)

    result = await db.execute(query)
    materials = result.scalars().all()

    response = []
    for m in materials:
        stock = await _calc_stock(m.id, db)
        data = MaterialResponse.model_validate(m)
        data.current_stock = stock
        data.stock_status = _calc_status(stock, m.low_stock_threshold)
        response.append(data)
    return response


@router.get("/{material_id}", response_model=MaterialResponse)
async def get_material(
    material_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    material = await get_material_or_404(material_id, db)
    await get_member_role(
        material.project_id, current_user.id, db
    )  # любая роль = доступ
    stock = await _calc_stock(material_id, db)
    data = MaterialResponse.model_validate(material)
    data.current_stock = stock
    data.stock_status = _calc_status(stock, material.low_stock_threshold)
    return data


@router.post("/", response_model=MaterialResponse, status_code=status.HTTP_201_CREATED)
async def create_material(
    data: MaterialCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = await get_member_role(data.project_id, current_user.id, db)
    if role == ProjectRole.viewer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Read-only access"
        )

    material = Material(**data.model_dump())
    db.add(material)
    await db.commit()
    await db.refresh(material)
    response = MaterialResponse.model_validate(material)
    response.current_stock = 0.0
    response.stock_status = _calc_status(
        response.current_stock, material.low_stock_threshold
    )
    return response


@router.patch("/{material_id}", response_model=MaterialResponse)
async def update_material(
    material_id: int,
    data: MaterialUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    material = await get_material_or_404(material_id, db)
    role = await get_member_role(material.project_id, current_user.id, db)
    if role == ProjectRole.viewer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Read-only access"
        )

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(material, field, value)
    await db.commit()
    await db.refresh(material)
    stock = await _calc_stock(material_id, db)
    response = MaterialResponse.model_validate(material)
    response.current_stock = stock
    response.stock_status = _calc_status(stock, material.low_stock_threshold)
    return response


@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_material(
    material_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    material = await get_material_or_404(material_id, db)
    role = await get_member_role(material.project_id, current_user.id, db)
    if role == ProjectRole.viewer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Read-only access"
        )

    await db.delete(material)
    await db.commit()
