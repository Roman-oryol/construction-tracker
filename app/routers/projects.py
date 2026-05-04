from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.project import Project
from app.models.project_member import ProjectMember, ProjectRole
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.core.dependencies import get_current_user
from app.core.shortcuts import get_member_role

router = APIRouter(prefix="/projects", tags=["projects"])


async def _get_project(project_id: int, db: AsyncSession) -> Project:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    return project


@router.get("/", response_model=list[ProjectResponse])
async def get_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Project)
        .join(ProjectMember)
        .where(ProjectMember.user_id == current_user.id)
    )
    return result.scalars().all()


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await get_member_role(project_id, current_user.id, db)
    return await _get_project(project_id, db)


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = Project(**data.model_dump(), owner_id=current_user.id)
    db.add(project)
    await db.flush()

    member = ProjectMember(
        project_id=project.id,
        user_id=current_user.id,
        role=ProjectRole.owner,
    )
    db.add(member)
    await db.commit()
    await db.refresh(project)
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = await get_member_role(project_id, current_user.id, db)
    if role == ProjectRole.viewer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Read-only access"
        )

    project = await _get_project(project_id, db)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    await db.commit()
    await db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = await get_member_role(project_id, current_user.id, db)
    if role != ProjectRole.owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only owner can delete"
        )

    project = await _get_project(project_id, db)
    await db.delete(project)
    await db.commit()
