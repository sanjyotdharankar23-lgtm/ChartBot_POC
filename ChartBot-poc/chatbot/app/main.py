from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .database import get_db, engine
from . import models
from .routers import chat, admin
from .auth import get_current_user

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Access Control Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

@app.get("/")
async def root():
    return {"message": "Access Control Chatbot API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}