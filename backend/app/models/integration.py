from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from app.core.database import Base

class Integration(Base):
    __tablename__ = "integrations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False) # ad_ldap, proxmox, nut, custom
    host = Column(String(255), nullable=False)
    port = Column(Integer, nullable=True)
    encrypted_payload = Column(Text, nullable=False) # JSON payload encrypted with Fernet
    is_enabled = Column(Boolean, default=True)
    status = Column(String(50), default="unknown") # online, offline, error, unconfigured
    last_synced = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class AppBookmark(Base):
    __tablename__ = "app_bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(255), default="")
    url = Column(String(500), nullable=False)
    icon = Column(String(50), default="terminal") # lucide icon name or neon glyph id
    color = Column(String(30), default="#00f3ff")
    target = Column(String(20), default="_blank") # _blank or hud_frame
    display_order = Column(Integer, default=0)
    group_name = Column(String(100), default="Основное")
    is_active = Column(Boolean, default=True)
