# Deps
import uuid
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException, File, UploadFile
from prisma import Prisma

# Methods
from src.routes.helpers.methods import is_invalid_data, is_int_value, is_valid_name

# Models
from src.routes.models.user import RoleByValue, GetPermissionsModel, PermissionsModel, DeleteInviteWorkspace, GetWorkspaceByAccess, RoleModel, GiveWorkspaceAccess, DeleteWorkspace, GetWorkspace, UserModel, EditModel, ModifyWorkspace, CreateWorkspace

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

# ___USER GENERALS___


@userRouter.post("/user/create/role", tags=["user"])
async def create_role(role_body: RoleModel):
    """
        We need to avoid users to create roles with
        special characters, should we handle this by
        frontend?
    """
    if not is_valid_name(role_body.roleName) or not is_int_value(role_body.roleValue):
        return {
            "message": "backend.errors.body.prop_missing_or_not_valid",
            "status": 500
        }

    db = Prisma()
    await db.connect()

    already_role_exist = await db.roles.find_first(
        where={
            "OR": [
                {"roleName": role_body.roleName},
                {"roleValue": role_body.roleValue}
            ]
        }
    )

    if already_role_exist:
        if already_role_exist.roleName == role_body.roleName or already_role_exist.roleValue == role_body.roleValue:
            return {
                "message": "backend.errors.body.already_exist",
                "status": 409,
            }

    await db.roles.create(
        data={
            "roleName": role_body.roleName,
            "roleValue": role_body.roleValue,
        }
    )

    return {
        "message": "backend.success.role.created",
        "status": 200,
    }


@userRouter.delete("/user/delete/role", tags=["user"])
async def delete_workspace(role_body: RoleByValue):
    if not role_body.roleValue:
        return {
            "message": "backend.errors.body.prop_missing_or_not_valid",
            "status": 500
        }

    db = Prisma()
    await db.connect()

    role_exist = await db.roles.find_unique(
        where={
            "roleValue": role_body.roleValue
        }
    )

    if not role_exist:
        await db.disconnect()
        return {
            "message": "backend.success.role.not_found",
            "status": 404,
        }

    await db.roles.delete(
        where={
            "roleValue": role_body.roleValue
        }
    )
    return {
        "message": "backend.success.role.deleted",
        "status": 200,
    }


@userRouter.post("/user/create/permissions", tags=["user"])
async def create_permission(post_permissions_body: PermissionsModel):
    if post_permissions_body.permissionsType is None and not post_permissions_body.permissionsLabel:
        return {
            "message": "backend.errors.body.prop_missing",
            "status": 400
        }

    db = Prisma()
    await db.connect()

    exist_permission = await db.permissions.find_unique(
        where={
            "permissionsType": post_permissions_body.permissionsType
        }
    )

    if exist_permission is not None:
        await db.disconnect()
        return {
            "message": "backend.alerts.permissions.already_exist",
            "status": 409,
        }

    created_permission = await db.permissions.create(
        data={
            "permissionsType": post_permissions_body.permissionsType,
            "permissionsLabel": post_permissions_body.permissionsLabel
        }
    )

    await db.disconnect()

    return {
        "message": "backend.success.permissions.success",
        "status": 201,
        "data": created_permission
    }


@userRouter.get("/user/get/permissions", tags=["user"])
async def get_permissions(post_permissions_body: GetPermissionsModel):
    print(post_permissions_body)
    if not post_permissions_body.permissionId:
        return {
            "message": "backend.alert.permissions.prop_missing",
            "status": 400
        }

    db = Prisma()
    await db.connect()

    if post_permissions_body.permissionId:
        permission = await db.permissions.find_unique(
            where={"id": post_permissions_body.permissionId}
        )
        await db.disconnect()

        if not permission:
            return {
                "message": "backend.errors.permissions.not_found",
                "status": 404
            }

        return {
            "message": "backend.success.permissions.found",
            "status": 200,
            "data": permission
        }
    else:
        permissions = await db.permissions.find_many()
        await db.disconnect()

        return {
            "message": "backend.success.permissions.found_all",
            "status": 200,
            "data": permissions
        }


@userRouter.delete("/user/delete/permissions", tags=["user"])
async def delete_permission(delete_permissions_body: GetPermissionsModel):
    if not delete_permissions_body.permissionId:
        return {
            "message": "backend.alert.permissions.prop_missing",
            "status": 400
        }

    db = Prisma()
    await db.connect()

    existing = await db.permissions.find_unique(
        where={"id": delete_permissions_body.permissionId}
    )

    if not existing:
        return {
            "message": "backend.errors.permissions.not_found",
            "status": 404
        }

    await db.permissions.delete(
        where={"id": delete_permissions_body.permissionId}
    )

    await db.disconnect()

    return {
        "message": "backend.success.permissions.deleted",
        "status": 200
    }

# ___WORKSPACE ENDPOINTS___


@userRouter.delete("/user/delete/workspace", tags=["user"])
async def delete_workspace(deleteWorkspace: DeleteWorkspace):
    """
        Quick comment here, when we delete a workspace
        we should update the KPIs since this affects
        analytics
    """

    if not deleteWorkspace.workspaceId:
        return {
            "message": "backend.errors.body.prop_missing",
            "status": 500
        }

    db = Prisma()
    await db.connect()

    workspace = await db.workspaces.find_first(
        where={
            "id": deleteWorkspace.workspaceId
        }
    )

    if not workspace:
        await db.disconnect()
        return {
            "message": "backend.success.workspace.not_exist",
            "status": 500,
        }

    await db.workspaces.delete(
        where={
            "id": deleteWorkspace.workspaceId
        }
    )

    await db.disconnect()
    return {
        "message": "backend.success.workspace.delete",
        "status": 200,
    }


@userRouter.delete("/user/get/give/access/workspace", tags=["user"])
async def delete_give_access_workspace(delete_workspaces_by_access: DeleteInviteWorkspace):
    if not delete_workspaces_by_access.workspaceId:
        return {
            "message": "backend.errors.body.prop_missing",
            "status": 500
        }

    db = Prisma()
    await db.connect()

    exist_workspace_invite = await db.workspaceaccess.find_unique(
        where={
            "id": delete_workspaces_by_access.workspaceId
        }
    )

    if not exist_workspace_invite:
        await db.disconnect()
        return {
            "message": "backend.success.workspace.access.not_found",
            "status": 404
        }

    await db.disconnect()
    return {
        "message": "backend.success.workspace.delete",
        "status": 200
    }

"""
Frontend can send us a complete object no need to be a JSON, I need to test this
I don't want FE to transform between json and object all the time, I prefer this
to be controlled by BE

In other hands, should we allow this endpoint to edit Kpis? I think this is a little
bit more complex.

In other hands, forms and messages need to have something inside of the objects to be
a valid update.

"""


@userRouter.put("/user/put/workspace", tags=["user"])
async def modify_workspace(modifyWorkspace: ModifyWorkspace):

    if not modifyWorkspace.workspaceId or not modifyWorkspace.whoModify:
        return {
            "message": "backend.errors.body.prop_missing",
            "status": 400
        }

    if is_invalid_data(modifyWorkspace.forms) and is_invalid_data(modifyWorkspace.messages):
        return {
            "message": "backend.errors.body.optional_parameter_has_invalid_data",
            "status": 400
        }

    db = Prisma()
    await db.connect()
    now = datetime.now().isoformat()

    workspace_exist = await db.workspaces.find_unique(
        where={
            "id": modifyWorkspace.workspaceId
        }
    )

    if not workspace_exist:
        return {
            "message": "backend.errors.workspaces.not_found",
            "status": 500
        }

    update_data = {}

    if modifyWorkspace.whoModify:
        updated_identify = json.dumps({
            **workspace_exist.identify,
            "whoModified": modifyWorkspace.whoModify,
            "workspaceModifiedAt": now
        })
        update_data["identify"] = updated_identify

    if not is_invalid_data(modifyWorkspace.forms):
        update_data["forms"] = json.dumps(modifyWorkspace.forms)

    if not is_invalid_data(modifyWorkspace.messages):
        update_data["messages"] = json.dumps(modifyWorkspace.messages)

    if not update_data:
        return {"message": "No valid fields to update."}

    await db.workspaces.update(
        where={
            "id": modifyWorkspace.workspaceId
        },
        data={
            **update_data
        }

    )

    edited_workspace = await db.workspaces.find_unique(
        where={
            "id": modifyWorkspace.workspaceId
        }
    )

    return {
        "message": "backend.success.workspace.updated",
        "status": 200,
        "workspaceEdited": {
            "workspaceName": edited_workspace.workspaceName,
            "identify": edited_workspace.identify,
            "kpi": edited_workspace.kpi,
            "forms": edited_workspace.forms,
            "messages": edited_workspace.messages
        }
    }


"""
We don't need here a fallback return here because getAll is False by default
"""


@userRouter.get("/user/get/give/access/workspace", tags=["user"])
async def get_give_access_workspace(get_workspaces_by_access: GetWorkspaceByAccess):
    if not get_workspaces_by_access.userId:
        return {
            "message": "backend.errors.body.prop_missing",
            "status": 500
        }

    db = Prisma()
    await db.connect()

    if get_workspaces_by_access.getAll == False:
        invite_workspace = await db.workspaceaccess.find_first(
            where={"userId": get_workspaces_by_access.userId}
        )

        if invite_workspace is None:
            await db.disconnect()
            return {
                "message": "backend.success.workspace.access.not_exist",
                "status": 404
            }

        await db.disconnect()
        return {
            "message": "backend.success.workspace.invite.success",
            "status": 202,
            "invite_workspace": invite_workspace
        }

    else:
        invite_workspace = await db.workspaceaccess.find_many(
            where={"userId": get_workspaces_by_access.userId}
        )

        if invite_workspace is None:
            await db.disconnect()
            return {
                "message": "backend.success.workspace.access.not_exist",
                "status": 404
            }

        await db.disconnect()
        return {
            "message": "backend.success.workspace.invite.success",
            "status": 202,
            "invite_workspace": invite_workspace
        }


@userRouter.post("/user/create/give/access/workspace", tags=["user"])
async def give_workspace_access(give_workspace_access: GiveWorkspaceAccess):
    if not give_workspace_access.permissionsId or not give_workspace_access.workspaceId or not give_workspace_access.userId or not give_workspace_access.roleId:
        return {
            "message": "backend.errors.body.prop_missing",
            "status": 500
        }

    db = Prisma()
    await db.connect()

    already_invite_exist = await db.workspaceaccess.find_first(
        where={
            "workspaceId": give_workspace_access.workspaceId,
            "role": give_workspace_access.roleId,
            "userId": give_workspace_access.userId
        }
    )

    if already_invite_exist is not None:
        await db.disconnect()
        return {
            "message": "backend.alerts.workspace.already_exist",
            "status": 409,
        }

    await db.workspaceaccess.create(
        data={
            "workspaceId": give_workspace_access.workspaceId,
            "role": give_workspace_access.roleId,
            "userId": give_workspace_access.userId,
            "permissionsId": give_workspace_access.permissionsId
        }
    )

    await db.disconnect()
    return {
        "message": "backend.success.workspace.give_access",
        "status": 200,
    }


@userRouter.post("/user/create/workspace", tags=["user"])
async def create_workspace(create_workspace_body: CreateWorkspace):
    if not is_valid_name(create_workspace_body.workspaceName) or not create_workspace_body.userName or not create_workspace_body.userId:
        return {
            "message": "backend.errors.body.prop_missing_or_not_valid",
            "status": 500
        }

    db = Prisma()
    await db.connect()

    already_exist = await db.workspaces.find_first(
        where={
            "userId": create_workspace_body.userId,
            "workspaceName": create_workspace_body.workspaceName
        })

    if already_exist is not None and already_exist.workspaceName is not None:
        await db.disconnect()
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

    await db.disconnect()
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

    if get_workspace_body.workspaceId is not None and get_workspace_body.userId is not None:
        return {
            "message": "backend.errors.body.conflicting_parameters",
            "status": 400
        }

    if get_workspace_body.workspaceId is None and get_workspace_body.userId is None:
        return {
            "message": "backend.errors.body.prop_missing",
            "status": 400
        }

    db = Prisma()
    await db.connect()

    if get_workspace_body.workspaceId:
        workspace = await db.workspaces.find_unique(
            where={"id": get_workspace_body.workspaceId}
        )
        await db.disconnect()

        if not workspace:
            return {
                "message": "backend.success.workspace.not_exist",
                "status": 404
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
            }
        }

    elif get_workspace_body.userId:
        workspaces = await db.workspaces.find_many(
            where={"userId": get_workspace_body.userId}
        )
        await db.disconnect()

        if not workspaces:
            return {
                "message": "backend.success.workspace.not_exist",
                "status": 404,
            }

        return {
            "message": "backend.success.workspace.found",
            "status": 200,
            "workspacesList": workspaces
        }

    else:
        await db.disconnect()
        return {
            "message": "backend.errors.body.prop_missing",
            "status": 400
        }
