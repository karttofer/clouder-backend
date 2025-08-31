### Env - Initials configs to run the app
# OpenAi
```.env
OPENAI_API_KEY=<opean-ai-key>
OPENAI_BOT_ID=<bot-id>
```
# Prisma
```.env
DATABASE_URL=postgresql://<name>:<password>@<host>:<port>/<database_name>
```
# Email sender
```.env
SENDER_EMAIL=<email_sender>
SENDER_API_KEY=<email_sender_api> - SMTP key value
```

### Run Commands
You must follow these steps before starting the Uvicorn command. If you don't establish the Prisma connections first, the app will throw an error.
```shell
# Before create the enviroment for python
1. python3 -m venv venv // py -3.11 -m venv venv
2. source venv/bin/activate // venv\Scripts\activate

# After create the enviroment for python
1. pip install -r requirements.txt 
2. prisma generate

# Local enviroments (Not supabase)
3. prisma migrate dev
# For supabase (Supabase don't allow the migrate since the service is already running, we don't have this control, so we just need to do the deployment)
3. prisma migrate deploy

4. uvicorn main:app --reload
```

# Local PostgreSQL Connection
To run the application locally with your PostgreSQL, you need to set up the proper connections. For example, the DATABASE_URL must be filled with the correct data. The host is usually localhost, and the port is 5432 by default. For database_name, you need to create a database within the <name> user. This means you must switch to the <name> user and create the database there.
# FAQ

These are some questions and answers I asked myself, and then I answered them through extensive research.

### Should I create a new environment to run this project?

The quick answer is yes. You should always create a new environment for a new Python project. In this case, I encountered some errors and issues related to this, but the solution is simple: create a new environment and then run the `requirements.txt`.

It's important to remember that if you create a new environment, you should ALWAYS run the `requirements.txt` (This is a reminder for myself since I always forget this step).

### Why can't I find the PostgreSQL host/port on Ubuntu?

If you're new to Ubuntu, you should know that the configuration can be a bit more extensive (but not difficult). For this issue, I had a conversation with *ChatGPT*. You will need to go through the process to find the answer. In the future, I will include the correct procedure here.

[Link to ChatGPT conversation](https://chatgpt.com/share/9d1c5124-033d-47d7-b941-336bb3e4287a)

### Should I create my own ROLE in PostgreSQL?

The quick answer is yes. You will need to create the ROLE and Database. After putting all the information in the .env (PostgreSQL URL), you only need to run the commands provided in this README (Prisma commands in the "Run Commands" section).

### Future
- Implement Docker to run all the enviroment


