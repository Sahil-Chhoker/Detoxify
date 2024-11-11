from fastapi import FastAPI
from apis.base import api_router
from core.config import settings
from fastapi.middleware.cors import CORSMiddleware

def include_router(app):
    app.include_router(api_router)

def start_application():
    app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
    include_router(app)
    return app

app = start_application()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Home Page"}

"""
from client import SUPABASE
data_users = [
    {"name": "John Doe", "email": "fKxHt@example.com", "password": "password123"},
    {"name": "Jane Doe", "email": "9kx0V@example.com", "password": "password456"},
    {"name": "Bob Smith", "email": "9kxV@example.com", "password": "password789"},
]

data_accounts = [
    {
        "id": "3c30faa8-fe18-49f9-a283-5f26615902c9",
        "youtube_username": "brother",
        "youtube_password": "password123",
    },
    {
        "id": "e58b0659-8583-4fa5-9577-4336496b7c0d",
        "youtube_username": "sister",
        "youtube_password": "password456",
    },
]


def insert_data_users(data):
    try:
        response = SUPABASE.table("users").insert(data).execute()
        return response
    except Exception as exception:
        return exception


def insert_data_accounts(data):
    try:
        response = SUPABASE.table("accounts").insert(data).execute()
        return response
    except Exception as exception:
        return exception


account_response = insert_data_accounts(data=data_accounts)
print(account_response)
"""