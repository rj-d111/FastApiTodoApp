from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Date
from sqlalchemy.sql import func



class Users(Base):
    __tablename__ = 'users'
    
    id=Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String, default='user')  # Default role is 'user'
    birthdate = Column(Date)
    gender = Column(String, default ='other')
    phone_number = Column(String)
    country = Column(String)
    date_created = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    date_modified = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    
            
class Todos(Base):
    __tablename__ = 'todos'
    
    id=Column(Integer, primary_key=True, index=True)
    title=Column(String, nullable=False)
    description = Column(String)
    priority = Column(Integer)
    complete =Column(Boolean, default=False)
    archive = Column(Boolean, default=False)
    date_created = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    date_modified = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))