from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import create_access_token, get_password_hash, verify_password
from app.schemas.user import LoginRequest, TokenResponse, ChangePasswordRequest, UserResponse
from app.services.auth_service import authenticate_user
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    user, auth_source = await authenticate_user(db, req.username, req.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed: invalid credentials or AD bind rejected"
        )
    
    token = create_access_token(data={
        "sub": str(user.id),
        "username": user.username,
        "role": user.role
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "must_change_password": user.must_change_password,
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "auth_source": user.auth_source,
            "can_manage_integrations": user.can_manage_integrations,
            "can_manage_apps": user.can_manage_apps,
            "can_manage_panels": user.can_manage_panels,
            "must_change_password": user.must_change_password
        }
    }

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/change-password")
async def change_password(
    req: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.auth_source == "ad":
        raise HTTPException(status_code=400, detail="AD LDAP passwords must be changed in Active Directory")

    # If current_password is provided and user is not in forced-reset state, verify it
    if not current_user.must_change_password:
        if not req.current_password or not verify_password(req.current_password, current_user.hashed_password):
            raise HTTPException(status_code=400, detail="Current password incorrect")

    current_user.hashed_password = get_password_hash(req.new_password)
    current_user.must_change_password = False
    await db.commit()
    return {"success": True, "message": "Password updated successfully"}
