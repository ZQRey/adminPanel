from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Panel(Base):
    __tablename__ = "panels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), default="")
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True) # None = global system default template
    is_default = Column(Boolean, default=False)
    is_system_template = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    widgets = relationship("Widget", back_populates="panel", cascade="all, delete-orphan", lazy="selectin")

class Widget(Base):
    __tablename__ = "widgets"

    id = Column(Integer, primary_key=True, index=True)
    panel_id = Column(Integer, ForeignKey("panels.id"), nullable=False)
    type = Column(String(50), nullable=False) # clock, weather, proxmox, nut, plugin
    title = Column(String(100), nullable=False)
    is_system = Column(Boolean, default=False) # System widget: locked / cannot be deleted by standard user
    grid_col = Column(Integer, default=1)
    grid_row = Column(Integer, default=1)
    col_span = Column(Integer, default=1)
    row_span = Column(Integer, default=1)
    config = Column(Text, default="{}") # JSON config string

    panel = relationship("Panel", back_populates="widgets")
