# Steps to be able to complete the bot
# 1. To create a conversation we need to create a thread
#
#
#
# Deps
from fastapi import APIRouter, HTTPException, status
from prisma import Prisma

# Bot helpers
from src.openAi.main import (
    create_bot_threads,
    create_user_message,
    get_conversation_list,
    delete_bot_thread,
)

# Models
from src.routes.models.bot import (
    CreateThreadModelMessagesModel,
    SendMessageModel,
    MessageListBodyModel,
    DeleteThreadModel,
)

botRouter = APIRouter()

@botRouter.post("/bot/create-conversation", tags=["bot"])
async def create_conversation(createConversationBody: CreateThreadModelMessagesModel):
    db = Prisma()
    try:
        await db.connect()

        threads = create_bot_threads(createConversationBody.messages)
        
        await db.userthreads.create(
            data={
                "thread_id": threads.id,
                "user_id": createConversationBody.user_id,
                "thread_name": createConversationBody.thread_name,
                "created_at": threads.created_at,
                "isArchived": False,
            }
        )
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        await db.disconnect()

    return {"message": "Conversation created", status: 200}


@botRouter.post("/bot/send-message", tags=["bot"])
def read_user(sendMessageBody: SendMessageModel):
    try:
        create_user_message(sendMessageBody)
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
    return {"message": "Message was created", status: 200}


@botRouter.delete("/bot/delete-thread", tags=["bot"])
async def read_user(deleteThreadBody: DeleteThreadModel):
    try:
        await delete_bot_thread(deleteThreadBody.thread_id)
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

    return {"message": "Conversation deleted", status: 200}


@botRouter.get("/bot/messages-list", tags=["bot"])
def read_user(messageListBody: MessageListBodyModel):
    return get_conversation_list({"thread_id": messageListBody.thread_id})
