from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import os
from configs.descriptions import bot_description, bot_instruction

# Manejar las variables de entorno
dotenv_patch = find_dotenv()
load_dotenv(dotenv_patch)

# Configuración de OpenAI
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

# Recuperar el asistente creado previamente
my_assistant_id = os.getenv("OPENAI_BOT_ID") 
my_assistant = client.beta.assistants.retrieve(my_assistant_id)

# Crear un nuevo hilo de conversación
message_thread = client.beta.threads.create(
  messages=[
    {
      "role": "user",
      "content": "How does AI work? Explain it in simple terms."
    },
  ]
) 

# run = client.beta.threads.runs.create(
#   thread_id=message_thread.id,
#   assistant_id=my_assistant_id
# )

# runs = client.beta.threads.runs.list(
# "thread_lFZnh9SylVk0nlj3mJIgumU2"
# )

response = client.beta.threads.messages.list("thread_lFZnh9SylVk0nlj3mJIgumU2")
print(response.data)
