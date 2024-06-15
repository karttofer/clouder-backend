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
SENDER_API_KEY=<email_sender_api>
```

### Run Commands
```shell
pip install -r requirements. txt 

prisma generate
prisma migrate dev

uvicorn main:app --reload
```
### FAQ

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


