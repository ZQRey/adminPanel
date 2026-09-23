from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_password_hash, generate_temp_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse, ResetPasswordResponse
from app.api.deps import require_admin, get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("", response_model=List[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    stmt = select(User).order_by(User.id.asc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("", response_model=UserResponse)
async def create_user(
    req: UserCreate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    # Only superadmin can create superadmin/admin roles
    if req.role in ["superadmin", "admin"] and admin_user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Only SuperAdmin can assign Admin or SuperAdmin roles")

    # Check unique username
    stmt = select(User).where(User.username == req.username)
    res = await db.execute(stmt)
    if res.scalars().first():
        raise HTTPException(status_code=400, detail="Username already exists")

    init_password = req.password or generate_temp_password()
    must_change = True if not req.password else False

    new_user = User(
        username=req.username,
        hashed_password=get_password_hash(init_password),
        role=req.role,
        auth_source="local",
        can_manage_integrations=req.can_manage_integrations,
        can_manage_apps=req.can_manage_apps,
        can_manage_panels=req.can_manage_panels,
        must_change_password=must_change,
        is_active=True
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    req: UserUpdate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    stmt = select(User).where(User.id == user_id)
    res = await db.execute(stmt)
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role == "superadmin" and admin_user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Only SuperAdmin can modify SuperAdmin accounts")

    if req.role is not None:
        if req.role == "superadmin" and admin_user.role != "superadmin":
            raise HTTPException(status_code=403, detail="Only SuperAdmin can grant SuperAdmin role")
        user.role = req.role

    if req.can_manage_integrations is not None:
        user.can_manage_integrations = req.can_manage_integrations
    if req.can_manage_apps is not None:
        user.can_manage_apps = req.can_manage_apps
    if req.can_manage_panels is not None:
        user.can_manage_panels = req.can_manage_panels
    if req.is_active is not None:
        user.is_active = req.is_active

    await db.commit()
    await db.refresh(user)
    return user

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    if user_id == admin_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own active account")

    stmt = select(User).where(User.id == user_id)
    res = await db.execute(stmt)
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role == "superadmin" and admin_user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Only SuperAdmin can delete SuperAdmin accounts")

    await db.delete(user)
    await db.commit()
    return {"success": True, "message": f"User {user.username} deleted"}

@router.post("/{user_id}/reset-password", response_model=ResetPasswordResponse)
async def reset_password(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    stmt = select(User).where(User.id == user_id)
    res = await db.execute(stmt)
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    temp_password = generate_temp_password(12)
    user.hashed_password = get_password_hash(temp_password)
    user.must_change_password = True
    await db.commit()

    return {
        "username": user.username,
        "temporary_password": temp_password,
        "message": "Temporary password generated. User must change it upon next login."
    }
