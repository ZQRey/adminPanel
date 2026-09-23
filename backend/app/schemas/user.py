from typing import Optional
from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    must_change_password: bool
    user: dict

class UserCreate(BaseModel):
    username: str
    password: Optional[str] = None
    role: str = "user" # superadmin, admin, user
    can_manage_integrations: bool = False
    can_manage_apps: bool = False
    can_manage_panels: bool = False

class UserUpdate(BaseModel):
    role: Optional[str] = None
    can_manage_integrations: Optional[bool] = None
    can_manage_apps: Optional[bool] = None
    can_manage_panels: Optional[bool] = None
    is_active: Optional[bool] = None

class ChangePasswordRequest(BaseModel):
    current_password: Optional[str] = None
    new_password: str

class ResetPasswordResponse(BaseModel):
    username: str
    temporary_password: str
    message: str

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    auth_source: str
    can_manage_integrations: bool
    can_manage_apps: bool
    can_manage_panels: bool
    must_change_password: bool
    is_active: bool

    class Config:
        from_attributes = True
