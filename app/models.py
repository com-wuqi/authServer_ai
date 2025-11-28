from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class UserBase(SQLModel):
    """用户基础模型"""
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False

class User(UserBase, table=True):
    """用户数据库模型"""
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(SQLModel):
    """用户创建模型"""
    username: str
    email: str
    full_name: Optional[str] = None
    password: str

class UserRead(UserBase):
    """用户读取模型"""
    id: int
    created_at: datetime
    updated_at: datetime

class UserUpdate(SQLModel):
    """用户更新模型"""
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class Token(SQLModel):
    """Token响应模型"""
    access_token: str
    token_type: str

class TokenData(SQLModel):
    """Token数据模型"""
    username: Optional[str] = None