# TODO: Refactor everything related to this file
# TODO: CRUD Workspace

# Deps
import uuid
from fastapi import APIRouter, HTTPException, File, UploadFile
from prisma import Prisma
from prisma.types import UserWhereUniqueInput
import json

# Models
from src.routes.models.user import UserModel, EditModel, ModifyWorkspace, CreateWorkspace

# Utils
from src.routes.helpers.methods import workspace_template

# Auth
userRouter = APIRouter()


@userRouter.post("/user", tags=["user"])
async def read_user(userBody: UserModel):
    db = Prisma()

    if userBody.email == None:
        await db.disconnect()
        return [{"message": "Email is required", "code": 400}]
    try:
        await db.connect()

        user = await db.user.find_unique(where={"email": userBody.email})

        if user == None or user.nickname == None:
            return {"message": "User provider does not exist", "user_exist": False, "code": 404}
        return {"message": "User Exist", "user_exist": True, "data": user, "code": 200}

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        await db.disconnect()


@userRouter.post("/user/edit", tags=["user"])
async def edit_user(editBody: EditModel):
    db = Prisma()
    try:
        await db.connect()

        update_data = {
            field: value
            for field, value in editBody.model_dump().items()
            if value and field not in ["password", "id"]
        }

        if editBody.name or editBody.email:
            existing_user = await db.user.find_unique(where=update_data)

            if existing_user and existing_user.id:
                raise HTTPException(
                    status_code=409,
                    detail="User with the provided name or email already exists",
                )

        await db.user.update(where={"id": editBody.id}, data=update_data)

        return [{"message": "User details changed", "code": 200}]

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        await db.disconnect()


@userRouter.post("/user/upload/image", tags=["user"])
async def read_user(file: UploadFile = File(...)):
    # Give unique name to the file
    file.filename = f"{uuid.uuid4()}.png"

    # Read the content of the file    
    fileContent = await file.read()

    # Save the file
    with open(f"src/uploads/{file.filename}", "wb") as f:
        f.write(fileContent)

    return [{"message": {
        "status": 200,
        "data": {
            "filename": file.filename,
            "content_type": file.content_type
        }
    }}]


@userRouter.put("/user/modify/workspace", tags=["user"])
async def read_user(modifyWorkspace: ModifyWorkspace):
    print("")


from datetime import datetime

from datetime import datetime


@userRouter.post("/user/create/workspace", tags=["user"])
async def create_workspace(create_workspace_body: CreateWorkspace):
    db = Prisma()
    await db.connect()

    now = datetime.utcnow().isoformat()

    await db.workspaces.create(
        data={
            "workspaceName": create_workspace_body.workspace_name,
            "identify": json.dumps({
                "workspaceCreateAt": "",
                "workspaceModifiedAt": "",
                "whoModified": "",
                "whoCreated": create_workspace_body.user_name
            }),
            "kpi": json.dumps([
                {
                    "label": "kpis.dashboard.completion_rate",
                    "value": "0%",
                    "delta": 0
                },
                {
                    "label": "kpis.dashboard.active_forms",
                    "value": "0",
                    "delta": 0
                },
                {
                    "label": "kpis.dashboard.responses_today",
                    "value": "0",
                    "delta": 0
                },
                {
                    "label": "kpis.dashboard.pending_candidates",
                    "value": "0",
                    "delta": 0
                }
            ]),
            "forms": json.dumps([{}]),
            "messages": json.dumps([{}]),
            "userId": create_workspace_body.user_token
        }
    )
