# Deps
import uuid
from fastapi import APIRouter, HTTPException, File, UploadFile
from prisma import Prisma

# Models
from src.routes.models.user import UserModel, EditModel

# Auth
from src.routes.auth import salt_password

userRouter = APIRouter()


@userRouter.get("/user", tags=["user"])
async def read_user(userBody: UserModel):
    db = Prisma()

    try:
        await db.connect()

        user = await db.user.find_unique(where={"id": userBody.id})
        print(user)
        if user == None or user.nickname == None:
            return HTTPException(
                status_code=404,
                detail="User with details provided does no exist",
            )
        return [{"message": "User Exist", "data": user, "code": 200}]

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

        if editBody.nickname or editBody.email:
            existing_user = await db.user.find_unique(where=update_data)

            if existing_user and existing_user.id:
                raise HTTPException(
                    status_code=409,
                    detail="User with the provided nickname or email already exists",
                )

        if editBody.password:
            update_data["password"] = salt_password(editBody.password)

        await db.user.update(where={"id": editBody.id}, data=update_data)

        return [{"message": "User details changed", "code": 200}]

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        await db.disconnect()


@userRouter.post("/user/conversations", tags=["user"])
def read_user():
    return [{"message": "auth-magic-link"}]


@userRouter.post("/user/archived-conversations", tags=["user"])
def read_user():
    return [{"message": "auth-magic-link"}]


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
