import re
from fastapi import APIRouter, Depends, HTTPException, Path
from ..models import Todos, Users
from pydantic import BaseModel, Field
from ..database import   SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session 
from starlette import status
from datetime import datetime, timezone
from .auth import get_current_user
from passlib.context import CryptContext

  
router = APIRouter(
    prefix="/users",
    tags=["users"],

)

 
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency =  Annotated[Session, Depends(get_db)]      
user_dependency = Annotated[dict, Depends(get_current_user)]  
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')  # Fixed: schema -> schemes, bycrypt -> bcrypt


class UserVerification(BaseModel):
    password: str = Field(min_length=6)
    new_password: str = Field(min_length=6)

    class Config:
        json_schema_extra = {
            "example": {
                "password": "current_pass",
                "new_password": "new_pass"
            }
        }

@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_users(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    return db.query(Users).filter(Users.id == user.get("id")).all()


@router.get("/todos", status_code=status.HTTP_200_OK)
async def read_all_todos(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()

@router.delete("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is not None:
        db.delete(todo_model)
        db.commit()
        return {"detail": "Todo deleted successfully"}
    raise HTTPException(status_code=404, detail='Todo not found')
                      
@router.put("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    
    current_user = db.query(Users).filter(Users.id == user.get('id')).first()
    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if not bcrypt_context.verify(user_verification.password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
    
    new_hashed_password = bcrypt_context.hash(user_verification.new_password)
    current_user.hashed_password = new_hashed_password
    db.commit()
    
    return {"detail": "Password updated successfully"}

@router.put("/phonenumber/{phonenumber}", status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(user: user_dependency, db: db_dependency, phonenumber: str):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if not user_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Validate phone number format (optional)
    if not re.match(r'^\d{11}$', phonenumber):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid phone number format")
    
    user_model.phone_number = phonenumber
    db.commit()
    
    return {"detail": "Phone number updated successfully"}