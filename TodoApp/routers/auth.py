from ..models import Users
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from datetime import date, datetime, timezone, timedelta 
from typing import Optional
from fastapi.responses import JSONResponse
from enum import Enum
import json
import re
from fastapi import APIRouter, Depends, HTTPException, Path, Request
from typing import Annotated
from sqlalchemy.orm import Session 
from ..database import   SessionLocal
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi.templating import Jinja2Templates


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')  # Fixed: schema -> schemes, bycrypt -> bcrypt
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

SECRET_KEY = "181d36c5f4f1377b9f0b95ea8b7a18f0768d1994e0d8b359cce102bc657beb35"
ALGORITHM = "HS256"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency =  Annotated[Session, Depends(get_db)]        

templates = Jinja2Templates(directory="TodoApp/templates")  # Adjust the path as necessary

### Pages ###
@router.get("/login-page") 
def render_login_page(request: Request):
    user = None
    try:
        user = get_current_user(request)
    except Exception:
       pass
                     
    return templates.TemplateResponse("login.html", {"request": request, "user": user})

@router.get("/register-page") 
def render_register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "countries": countries})
 

### Endpoints ###

def authenticate_user(username: str, password: str, db) -> Optional[Users]:
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        print("User not found")
        return None
    if not bcrypt_context.verify(password, user.hashed_password):
        print("Wrong password")
        return None
    return user

def create_access_token(user: str, user_id: int, role: str,  expires_delta: Optional[timedelta] = None):
    encode = {'sub': user, 'id': user_id, 'role': role}
    expires = datetime.utcnow() + expires_delta  
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token provided")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")
        return {"username": username, "id": user_id, "role": user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")    

with open("TodoApp/data/countries.json", "r") as file:
    countries = json.load(file)
    

def create_country_enum():
    enum_values ={}
    for country in countries:
        country_name = country['name']
        enum_key = re.sub(r'[^a-zA-Z0-9_]', '_', country_name).upper()
        enum_values[enum_key] = country_name
    return Enum('Country', enum_values, type=str) 
    
Country = create_country_enum()





class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"
    GUEST = "guest"
    
class Gender(str, Enum):
    MALE = "male" 
    FEMALE = "female"
    OTHER = "other"

class Token(BaseModel):
    access_token: str
    token_type: str  


class CreateUserRequest(BaseModel):
    username: str 
    email: str 
    first_name: str 
    last_name: str 
    password: str 
    phone_number: str
    gender: Gender = Field(default=Gender.OTHER)
    role: UserRole = Field(default=UserRole.USER)
    is_active: bool = True 
    birthdate: date = Field(gt=date(1900, 1, 1), lt=date.today()) 
    created_at: datetime | None = None
    modified_at: datetime | None = None
    country: Country = Field(default=Country.PHILIPPINES)  # Default to Philippines
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "example@gmail.com",
                "first_name": "John",
                "last_name": "Doe",
                "password": "securepassword",
                "phone_number": "09123456789",
                "gender": "male",
                "role": "user",
                "birthdate": "1990-01-01",
                "country" : "Philippines",
                "is_active": True,
            }
    }   
  

@router.post("/", status_code=status.HTTP_201_CREATED) 
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    create_user_model = Users(
                              email = create_user_request.email,
                              username = create_user_request.username,
                              last_name = create_user_request.last_name,
                              first_name = create_user_request.first_name,
                              country = create_user_request.country,
                              birthdate = create_user_request.birthdate,
                              is_active = create_user_request.is_active,
                              gender = create_user_request.gender,
                              phone_number = create_user_request.phone_number,
                              date_created = datetime.now(timezone.utc),  # Set creation time
                              date_modified=datetime.now(timezone.utc),  # Set modification time 
                              role = create_user_request.role,
                              hashed_password = bcrypt_context.hash(create_user_request.password),
                              )
    db.add(create_user_model)
    db.commit()
 
class LoginRequest(BaseModel):
    username: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "username": "username",
                "password": "securepassword"
            },
            "properties": {
                "username": {"type": "string", "format": "email", "description": "Enter your email address here"},
                "password": {"type": "string", "format": "password", "description": "Enter your password here"}
            }
        }   
    
@router.post("/token", response_model=Token, status_code=status.HTTP_200_OK)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")
    token = create_access_token(user.username, user.id, user.role, expires_delta=timedelta(minutes=20))
    
    # Create a JSONResponse and set the cookie
    response = JSONResponse(content={"access_token": token, "token_type": "bearer"})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,  # Prevents JavaScript access to the cookie
        secure=False,   # Set to False for local development (use True in production with HTTPS)
        samesite="lax", # Protects against CSRF
        max_age=20 * 60,  # Cookie expires in 20 minutes
        path="/",       # Cookie available for all routes
    )
    return response