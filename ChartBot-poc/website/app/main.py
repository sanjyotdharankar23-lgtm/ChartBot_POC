from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .database import get_db, engine
from . import models
from .routers import access, bappas

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Access Control Website")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(access.router, prefix="/api/access", tags=["access"])
app.include_router(bappas.router, prefix="/api/bappas", tags=["bappas"])

@app.get("/")
async def root():
    return {"message": "Access Control Website API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}