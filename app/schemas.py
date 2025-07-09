# schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- Collaborators ---
class Collaborator(BaseModel):
    user_id: int
    role: str  # viewer, editor, owner

# --- Tasks ---
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    owner_id: int
    collaborators: List[Collaborator] = []
    role: Optional[str] = None  # Added for dashboard view

    class Config:
        from_attributes = True
