from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List

from ..database import get_session
from ..models import User, UserRead, UserUpdate
from ..auth import get_current_superuser, get_user_by_username, get_user_by_email, get_password_hash

router = APIRouter(prefix="/users", tags=["用户管理"])

@router.get("/", response_model=List[UserRead])
def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_session)
):
    """获取用户列表（仅管理员）"""
    statement = select(User).offset(skip).limit(limit)
    users = db.exec(statement).all()
    return users

@router.get("/{user_id}", response_model=UserRead)
def read_user(
    user_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_session)
):
    """获取指定用户（仅管理员）"""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return user

@router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_session)
):
    """更新指定用户（仅管理员）"""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 检查用户名是否与其他用户冲突
    if user_update.username and user_update.username != user.username:
        existing_user = get_user_by_username(db, user_update.username)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )

    # 检查邮箱是否与其他用户冲突
    if user_update.email and user_update.email != user.email:
        existing_user = get_user_by_email(db, user_update.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在"
            )

    # 更新字段
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == 'password' and value:
            setattr(user, 'hashed_password', get_password_hash(value))
        elif value is not None:
            setattr(user, field, value)

    user.updated_at = user.updated_at.now()
    db.add(user)
    db.commit()
    db.refresh(user)

    return user

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_session)
):
    """删除指定用户（仅管理员）"""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 防止管理员删除自己
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账户"
        )

    db.delete(user)
    db.commit()

    return {"message": "用户删除成功"}

@router.post("/{user_id}/toggle-active")
def toggle_user_active(
    user_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_session)
):
    """启用/禁用用户（仅管理员）"""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 防止管理员禁用自己
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能禁用自己的账户"
        )

    user.is_active = not user.is_active
    user.updated_at = user.updated_at.now()
    db.add(user)
    db.commit()

    status_text = "启用" if user.is_active else "禁用"
    return {"message": f"用户已{status_text}"}