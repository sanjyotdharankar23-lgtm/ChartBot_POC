from fastapi import FastAPI, Depends, Request, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .database import get_db
from . import models
from .routers import access, bappas
from .auth import get_current_user, verify_login

# Create database tables
engine = create_engine("postgresql://admin:password@postgres:5432/access_control")
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Access Control Website", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(access.router, prefix="/api/access", tags=["access"])
app.include_router(bappas.router, prefix="/api/bappas", tags=["bappas"])

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    user = verify_login(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # In production, create proper JWT token
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(key="access_token", value=username)
    return response

@app.get("/user-access", response_class=HTMLResponse)
async def user_access_page(request: Request, current_user: dict = Depends(get_current_user)):
    return templates.TemplateResponse("user_access.html", {"request": request, "user": current_user})

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "access-control-website"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)