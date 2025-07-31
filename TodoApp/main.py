from fastapi import FastAPI, Depends, HTTPException, Path, Request, status
from .models import Base  
from pydantic import BaseModel, Field
from .database import engine, SessionLocal
from typing import Annotated
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from starlette import status
from datetime import datetime, timezone
from .routers import auth, todos, admin, users
from fastapi.templating import Jinja2Templates 
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import RedirectResponse

app = FastAPI()


Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="TodoApp/templates")  

app.mount("/static", StaticFiles(directory="TodoApp/static"), name="static")

app.add_middleware(GZipMiddleware)


@app.get("/")
def test(request: Request):
    return RedirectResponse(url="/todos/todo-page", status_code=status.HTTP_302_FOUND)

@app.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/healthy")
def health_check():
    return {"status": "healthy"}





app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
 