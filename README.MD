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
```cmd
pip install -r requirements. txt 

prisma generate
prisma migrate dev

uvicorn main:app --reload
```

### Future
- Implement Docker to run all the enviroment


