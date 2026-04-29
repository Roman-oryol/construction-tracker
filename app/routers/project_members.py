from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.project_member import ProjectMember, ProjectRole
from app.models.user import User
from app.schemas.project_member import ProjectMemberAdd, ProjectMemberResponse
from app.core.dependencies import get_current_user
from app.routers.projects import _get_member_role

router = APIRouter(prefix="/projects/{project_id}/members", tags=["project members"])


@router.get("/", response_model=list[ProjectMemberResponse])
async def get_members(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _get_member_role(project_id, current_user.id, db)  # любая роль = доступ
    result = await db.execute(
        select(ProjectMember).where(ProjectMember.project_id == project_id)
    )
    return result.scalars().all()


@router.post(
    "/", response_model=ProjectMemberResponse, status_code=status.HTTP_201_CREATED
)
async def add_member(
    project_id: int,
    data: ProjectMemberAdd,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = await _get_member_role(project_id, current_user.id, db)
    if role != ProjectRole.owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only owner can add members"
        )

    # Проверяем что такой юзер существует
    result = await db.execute(select(User).where(User.id == data.user_id))
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Проверяем что юзер ещё не в проекте
    result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == data.user_id,
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already a member"
        )

    member = ProjectMember(project_id=project_id, user_id=data.user_id, role=data.role)
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return member


@router.patch("/{user_id}", response_model=ProjectMemberResponse)
async def update_member_role(
    project_id: int,
    user_id: int,
    data: ProjectMemberAdd,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = await _get_member_role(project_id, current_user.id, db)
    if role != ProjectRole.owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only owner can change roles"
        )

    result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Member not found"
        )
    if member.role == ProjectRole.owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Cannot change owner role"
        )

    member.role = data.role
    await db.commit()
    await db.refresh(member)
    return member


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    project_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = await _get_member_role(project_id, current_user.id, db)
    if role != ProjectRole.owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner can remove members",
        )

    result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Member not found"
        )
    if member.role == ProjectRole.owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Cannot remove owner"
        )

    await db.delete(member)
    await db.commit()
