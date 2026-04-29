from pydantic import BaseModel, ConfigDict
from app.models.project_member import ProjectRole


class ProjectMemberAdd(BaseModel):
    user_id: int
    role: ProjectRole = ProjectRole.viewer


class ProjectMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    user_id: int
    role: ProjectRole
