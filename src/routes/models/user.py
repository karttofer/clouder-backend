# Deps
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class UserModel(BaseModel):
    email: str


class EditModel(BaseModel):
    id: str
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class ModifyWorkspace(BaseModel):
    workspaceId: str
    whoModify: str = ""
    workspaceName: str = ""
    forms: List[Dict[str, Any]] = Field(default_factory=lambda: [{}])
    messages: List[Dict[str, Any]] = Field(default_factory=lambda: [{}])


class CreateWorkspace(BaseModel):
    workspaceName: str = ""
    userId: str


class GetWorkspace(BaseModel):
    workspaceId: Optional[str] = ""
    userId: Optional[str] = ""


class DeleteWorkspace(BaseModel):
    workspaceId: str


class GiveWorkspaceAccess(BaseModel):
    userEmail: str
    workspaceId: str
    permissionsId: str


class GetWorkspaceByAccess(BaseModel):
    userId: str
    getAll: bool = False


class DeleteInviteWorkspace(BaseModel):
    workspaceAccessId: str
    userInvitesId: str
    hasAccepted: bool = False


class RoleModel(BaseModel):
    roleName: str
    roleValue: int

# This should be roleType not roleValue


class RoleByValue(BaseModel):
    roleValue: int


class PermissionsModel (BaseModel):
    permissionsType: int
    permissionsLabel: str


class GetPermissionsModel (BaseModel):
    permissionId: str = ""
