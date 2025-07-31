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


# Create workspace - Identify model
class IdentifyWorkspaceModel(BaseModel):
    workspaceCreateAt: datetime = Field(default_factory=datetime.utcnow)
    workspaceModifiedAt: datetime = Field(default_factory=datetime.utcnow)
    whoModified: str = ''
    whoCreated: str = ''


# Create workspace - KPi workspace model
class KpiWorkspaceModel(BaseModel):
    workspaceCreateAt: datetime = Field(default_factory=datetime.utcnow)
    workspaceModifiedAt: datetime = Field(default_factory=datetime.utcnow)
    whoModified: str = ''
    whoCreated: str = ''


class ThemeSelectedModel(BaseModel):
    type: str = 'default'
    index: int = 0


class ThemesModel(BaseModel):
    # We need to type this one
    # Default theme will be in the Core column with default themes
    default: List[Any] = []

    # Custom is empty since it's for creation
    custom: List[Any] = []


class FormThemeModel(BaseModel):
    themeSelected: ThemeSelectedModel = ThemeSelectedModel()
    themes: ThemesModel = ThemesModel()

    # Now, this one is important since, when
    # The user selects a theme, we need to save the whole object config
    selectedThemeStyles: Dict[str, Any] = {}


class FormModel(BaseModel):
    projectName: str = ''
    lastSaved: str = ''
    history: List[str] = []
    formFields: List[str] = ['form_group']
    parentFieldIndex: int = 0
    childFieldIndex: Optional[int] = None
    historyIndexNav: int = 0
    formTheme: FormThemeModel = FormThemeModel()


class ModifyWorkspace(BaseModel):
    workspaceName: str = ""
    identify: IdentifyWorkspaceModel = IdentifyWorkspaceModel()
    kpi: List[KpiWorkspaceModel] = []
    forms: List[FormModel] = [FormModel()]


class CreateWorkspace(BaseModel):
    workspaceName: str = ""
    userId: str
    userName: str


class GetWorkspace(BaseModel):
    workspaceName: str = ""
    userId: str


class GetWorkspaces(BaseModel):
    userId: str
