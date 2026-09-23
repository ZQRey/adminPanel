from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class IntegrationConfig(BaseModel):
    # Active Directory
    base_dn: Optional[str] = None
    admin_dn: Optional[str] = None
    admin_password: Optional[str] = None
    use_ssl: Optional[bool] = False
    
    # Proxmox
    user: Optional[str] = None
    token_name: Optional[str] = None
    token_value: Optional[str] = None
    password: Optional[str] = None
    node: Optional[str] = "pve"
    verify_ssl: Optional[bool] = False
    
    # NUT
    ups_name: Optional[str] = "ups"
    nut_user: Optional[str] = None
    nut_password: Optional[str] = None

class IntegrationCreate(BaseModel):
    name: str
    type: str # ad_ldap, proxmox, nut, custom
    host: str
    port: Optional[int] = None
    config: Dict[str, Any] = {}
    is_enabled: bool = True

class IntegrationUpdate(BaseModel):
    name: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    config: Optional[Dict[str, Any]] = None
    is_enabled: Optional[bool] = None

class IntegrationResponse(BaseModel):
    id: int
    name: str
    type: str
    host: str
    port: Optional[int] = None
    is_enabled: bool
    status: str
    last_synced: Optional[datetime] = None
    has_secret: bool = True
    config_summary: Dict[str, Any] = {}

    class Config:
        from_attributes = True

class TestConnectionResponse(BaseModel):
    success: bool
    message: str
    latency_ms: Optional[float] = None
    details: Optional[Dict[str, Any]] = None

class AppBookmarkCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    url: str
    icon: Optional[str] = "terminal"
    color: Optional[str] = "#00f3ff"
    target: Optional[str] = "_blank"
    display_order: Optional[int] = 0
    group_name: Optional[str] = "Основное"

class AppBookmarkUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    target: Optional[str] = None
    display_order: Optional[int] = None
    group_name: Optional[str] = None
    is_active: Optional[bool] = None

class AppBookmarkResponse(BaseModel):
    id: int
    title: str
    description: str
    url: str
    icon: str
    color: str
    target: str
    display_order: int
    group_name: Optional[str] = "Основное"
    is_active: bool

    class Config:
        from_attributes = True
