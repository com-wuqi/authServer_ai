from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from datetime import timedelta

from ..database import get_session
from ..models import User, UserCreate, UserRead, Token
from ..auth import (
    get_password_hash, authenticate_user, create_access_token,
    get_user_by_username, get_user_by_email, get_current_active_user
)

router = APIRouter(prefix="/auth", tags=["认证"])

@router.post("/register", response_model=UserRead)
def register(user: UserCreate, db: Session = Depends(get_session)):
    """用户注册"""
    # 检查用户名是否已存在
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # 检查邮箱是否已存在
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已存在"
        )

    # 创建新用户
    try:
        hashed_password = get_password_hash(user.password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_session)
):
    """用户登录"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserRead)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    """获取当前用户信息"""
    return current_user

@router.put("/me", response_model=UserRead)
def update_user_me(
    user_update: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """更新当前用户信息"""
    # 检查用户名是否与其他用户冲突
    if 'username' in user_update and user_update['username'] != current_user.username:
        existing_user = get_user_by_username(db, user_update['username'])
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )

    # 检查邮箱是否与其他用户冲突
    if 'email' in user_update and user_update['email'] != current_user.email:
        existing_user = get_user_by_email(db, user_update['email'])
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在"
            )

    # 更新字段
    for field, value in user_update.items():
        if hasattr(current_user, field):
            if field == 'password':
                setattr(current_user, 'hashed_password', get_password_hash(value))
            else:
                setattr(current_user, field, value)

    current_user.updated_at = current_user.updated_at.now()
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return current_user