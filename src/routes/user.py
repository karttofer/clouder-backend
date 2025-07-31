# Deps
import uuid
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException, File, UploadFile
from prisma import Prisma

# Models
from src.routes.models.user import GetWorkspaces, GetWorkspace, UserModel, EditModel, ModifyWorkspace, CreateWorkspace

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


# ___WORKSPACE ENDPOINTS___

@userRouter.post("/user/create/workspace", tags=["user"])
async def create_workspace(create_workspace_body: CreateWorkspace):
    db = Prisma()
    await db.connect()

    if not create_workspace_body.workspaceName or not create_workspace_body.userName or not create_workspace_body.userId:
        return {
            "message": "backend.errors.body.prop_missing",
            "status": 500
        }

    already_exist = await db.workspaces.find_first(
        where={
            "userId": create_workspace_body.userId,
            "workspaceName": create_workspace_body.workspaceName
        })

    if already_exist is not None and already_exist.workspaceName is not None:
        return {
            "message": "backend.errors.body.already_exist",
            "status": 409,
        }

    now = datetime.now().isoformat()

    await db.workspaces.create(
        data={
            "workspaceName": create_workspace_body.workspaceName,
            "identify": json.dumps({
                "workspaceCreateAt": now,
                "workspaceModifiedAt": now,
                "whoModified": "",
                "whoCreated": create_workspace_body.userName
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
            "userId": create_workspace_body.userId
        }
    )

    workspace_created = await db.workspaces.find_first(
        where={
            "userId": create_workspace_body.userId,
            "workspaceName": create_workspace_body.workspaceName
        }
    )

    return {
        "message": "backend.success.workspace.created",
        "status": 200,
        "created_workspace": {
            "id": workspace_created.id,
            "identify": workspace_created.identify,
            "kpi": workspace_created.kpi,
            "forms": workspace_created.forms,
            "messages": workspace_created.messages,
        },
    }


@userRouter.get("/user/get/workspace", tags=["user"])
async def get_workspace(get_workspace_body: GetWorkspace):
    db = Prisma()

    await db.connect()

    if not get_workspace_body.workspaceName or not get_workspace_body.userId:
        return {
            "message": "backend.errors.body.prop_missing",
            "status": 500
        }

    workspace = await db.workspaces.find_first(
        where={
            "workspaceName": get_workspace_body.workspaceName,
            "userId": get_workspace_body.userId
        }
    )

    if workspace is None:
        return {
            "message": "backend.success.workspace.not_exist",
            "status": 500,
        }

    return {
        "message": "backend.success.workspace.found",
        "status": 200,
        "workspace": {
            "id": workspace.id,
            "identify": workspace.identify,
            "kpi": workspace.kpi,
            "forms": workspace.forms,
            "messages": workspace.messages,
        },
    }


@userRouter.get("/user/get/workspaces", tags=["user"])
async def get_workspaces(get_workspace_body: GetWorkspaces):
    db = Prisma()

    await db.connect()

    if not get_workspace_body.userId:
        return {
            "message": "backend.errors.body.prop_missing",
            "status": 500
        }

    workspaces = await db.workspaces.find_many(
        where={
            "userId": get_workspace_body.userId
        }
    )

    if not workspaces:
        return {
            "message": "backend.success.workspace.not_exist",
            "status": 500,
        }

    return {
        "message": "backend.success.workspace.found",
        "workspacesList": workspaces,
        "status": 200,
    }
