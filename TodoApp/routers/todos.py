from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from ..models import Todos
from pydantic import BaseModel, Field
from ..database import   SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session 
from starlette import status
from datetime import datetime, timezone
from .auth import get_current_user
from starlette.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

 

templates = Jinja2Templates(directory="TodoApp/templates")  # Adjust the path as necessary
  
router = APIRouter(
    prefix="/todos",
    tags=["todos"],
)

 
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency =  Annotated[Session, Depends(get_db)]      
user_dependency = Annotated[dict, Depends(get_current_user)]  
   
class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str | None  = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool
    archive: bool
    date_created: datetime| None = None
    date_modified: datetime| None = None
    
    class Config:
        # Prevent users from setting date fields in Swagger
        json_schema_extra = {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "priority": 3,
                "complete": False,
                "archive": False
            }
        }


def redirect_to_login():
    # redirect_response = JSONResponse({"url": "/auth/login-page"}, status_code=status.HTTP_302_FOUND)
    redirect_response = RedirectResponse(url="/auth/login-page")
    redirect_response.delete_cookie("access_token")  # Clear the access token cookie
    return redirect_response


### Pages ###
@router.get("/todo-page")
async def render_todos_page(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request)  # Pass the request directly
        if user is None:
            print("No user found")
            return redirect_to_login()
        
        print(f"Authenticated user: {user}")
        todos = db.query(Todos).filter(Todos.owner_id == user.get('id')).all()
        return templates.TemplateResponse("todos.html", {"request": request, "todos": todos, "user": user})
    except Exception as e:
        print(f"Error in render_todos_page: {str(e)}")  # Log the specific error
        return redirect_to_login()
    
@router.get("/add-todo-page")
async def render_add_todo_page(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request)  # Pass the request directly
        if user is None:
            print("No user found")
            return redirect_to_login()
        
        print(f"Authenticated user: {user}")
        return templates.TemplateResponse("add-todo.html", {"request": request, "user": user})
    except Exception as e:
        print(f"Error in render_add_todo_page: {str(e)}")
        return redirect_to_login()
    

@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(request: Request, db: db_dependency, todo_id: int = Path(gt=0)):
    try:
        user = await get_current_user(request)  # Pass the request directly
        if user is None:
            print("No user found")
            return redirect_to_login()
        
        print(f"Authenticated user: {user}")
        todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
        if todo_model is None:
            raise HTTPException(status_code=404, detail='Todo not found')
        
        return templates.TemplateResponse("edit-todo.html", {"request": request, "todo": todo_model, "user": user})
    except Exception as e:
        print(f"Error in render_edit_todo_page: {str(e)}")
        return redirect_to_login()

### Endpoints ###
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()

@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail='Todo not found')
    
@router.post("/add-todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest):
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    # Prepare data, excluding date fields from user input
    todo_data = todo_request.model_dump(exclude={"date_created", "date_modified"})
    todo_model = Todos(
        **todo_data,
        date_created=datetime.now(timezone.utc),  # Set creation time
        date_modified=datetime.now(timezone.utc),  # Set initial modification time
        owner_id=user.get('id')  # Assuming user is a dict with 'id' key
    )
    
    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)  # Refresh to get updated fields (e.g., ID)
    return todo_model
    
@router.put("/edit-todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency,  todo_request: TodoRequest, todo_id: int = Path(gt=0) ):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")

    todo_model =  db.query(Todos).filter(Todos.id ==  todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete
    todo_model.archive = todo_request.archive
    todo_model.date_modified = datetime.now(timezone.utc)  # Update modification time    
    
    db.add(todo_model)
    db.commit() 
    db.refresh(todo_model)  # Refresh to get updated fields (e.g., ID)
    return todo_model
    
     
@router.delete("/delete-todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int= Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id ==user.get("id")).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found')
    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id ==user.get("id")).delete()
    
    db.commit() 