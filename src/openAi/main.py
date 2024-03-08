"""
1. When we create a new conversation a new thread should be created
2. This same thread will be used to send messages and then get Bot response
3. Usually we won't change the bot id since we will in charge to train it first

TODO: Create the initial system to create conversations
      1. New thread
      2. Send messages to the bot using the same thread
      3. Get bot response by thread_id

REMEMBER
      - Right now we are no implementing the save conversation in the cloud
        this is something that we will storage in the local user computer
        devil plan -> - we can implement it with users that pay hahaha -  

REMEMBER
      - Message has id too.
      - We need to give the context of the conversation to the box if we want to save conversations
"""

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


"""
TODO: We need to create a table for this one, since when the a conversation is created it need to be stored
"""


def create_bot_thread():
    user_new_thread = client.beta.threads.create()


def delete_bot_thread(thread_id):
    try:
        client.beta.threads.delete(thread_id)
    except NameError:
        return NameError


def create_user_message(thread_id):

    client.beta.threads.delete(thread_id)


def get_bot_response():
    user_previous_thread_created = client.beta.threads.retrieve("thread_abc123")

    return user_previous_thread_created
