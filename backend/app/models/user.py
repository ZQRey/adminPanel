from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True) # None for pure AD LDAP users if not synced
    role = Column(String(20), default="user", nullable=False) # superadmin, admin, user
    auth_source = Column(String(20), default="local") # local, ad
    
    # Granular permissions
    can_manage_integrations = Column(Boolean, default=False)
    can_manage_apps = Column(Boolean, default=False)
    can_manage_panels = Column(Boolean, default=False)
    
    must_change_password = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
