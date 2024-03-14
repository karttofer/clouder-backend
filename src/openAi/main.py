import time
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import os

dotenv_patch = find_dotenv()
load_dotenv(dotenv_patch)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

my_assistant_id = os.getenv("OPENAI_BOT_ID")
my_assistant = client.beta.assistants.retrieve(my_assistant_id)

def create_bot_threads(configs_list):
    return client.beta.threads.create_and_run(
        assistant_id="asst_HwokEd87OmJCno4lLrzLYd7a", thread={"messages": configs_list}
    )


def delete_bot_thread(thread_id):
    try:
       return client.beta.threads.delete(thread_id)
    except NameError:
        return NameError


def create_user_message(config_list):
    return client.beta.threads.messages.create(
        config_list.thread_id,
        role=config_list.role,
        content=config_list.content,
    )


def get_conversation_list(config_list):
    thread_messages = client.beta.threads.runs.create(
        thread_id=config_list["thread_id"],
        assistant_id="asst_HwokEd87OmJCno4lLrzLYd7a",
    )
    while True:
        run_status = client.beta.threads.runs.retrieve(
            thread_id=config_list["thread_id"], run_id=thread_messages.id
        )
        time.sleep(10)
        if run_status.status == "completed":
            messages = client.beta.threads.messages.list(
                thread_id=config_list["thread_id"]
            )
            return messages
        else:
            time.sleep(2)