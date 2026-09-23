from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.models.panel import Panel, Widget
from app.models.user import User
from app.schemas.panel import (
    PanelCreate, PanelUpdate, PanelResponse, PanelCloneRequest,
    WidgetCreate, WidgetUpdate, WidgetResponse
)
from app.api.deps import get_current_user, require_admin

router = APIRouter(prefix="/panels", tags=["panels"])

@router.get("", response_model=List[PanelResponse])
async def list_panels(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Admins can see all panels, standard users see their own panels + system templates
    if current_user.role in ["superadmin", "admin"]:
        stmt = select(Panel).options(selectinload(Panel.widgets)).order_by(Panel.id.asc())
    else:
        stmt = select(Panel).options(selectinload(Panel.widgets)).where(
            or_(Panel.owner_id == current_user.id, Panel.is_system_template == True)
        ).order_by(Panel.id.asc())
    
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("", response_model=PanelResponse)
async def create_panel(
    req: PanelCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not (current_user.can_manage_panels or current_user.role in ["superadmin", "admin"]):
        raise HTTPException(status_code=403, detail="Permission to create panels denied")

    new_panel = Panel(
        name=req.name,
        description=req.description,
        owner_id=current_user.id,
        is_default=req.is_default,
        is_system_template=False
    )
    db.add(new_panel)
    await db.commit()
    await db.refresh(new_panel)
    return new_panel

@router.get("/{panel_id}", response_model=PanelResponse)
async def get_panel(
    panel_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Panel).options(selectinload(Panel.widgets)).where(Panel.id == panel_id)
    res = await db.execute(stmt)
    panel = res.scalars().first()
    if not panel:
        raise HTTPException(status_code=404, detail="Panel not found")

    if panel.owner_id != current_user.id and not panel.is_system_template and current_user.role not in ["superadmin", "admin"]:
        raise HTTPException(status_code=403, detail="Access to this panel is restricted")

    return panel

@router.put("/{panel_id}", response_model=PanelResponse)
async def update_panel(
    panel_id: int,
    req: PanelUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Panel).options(selectinload(Panel.widgets)).where(Panel.id == panel_id)
    res = await db.execute(stmt)
    panel = res.scalars().first()
    if not panel:
        raise HTTPException(status_code=404, detail="Panel not found")

    if panel.owner_id != current_user.id and current_user.role not in ["superadmin", "admin"]:
        raise HTTPException(status_code=403, detail="Permission denied")

    if req.name is not None:
        panel.name = req.name
    if req.description is not None:
        panel.description = req.description
    if req.is_default is not None:
        panel.is_default = req.is_default

    await db.commit()
    await db.refresh(panel)
    return panel

@router.delete("/{panel_id}")
async def delete_panel(
    panel_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Panel).where(Panel.id == panel_id)
    res = await db.execute(stmt)
    panel = res.scalars().first()
    if not panel:
        raise HTTPException(status_code=404, detail="Panel not found")

    if panel.is_system_template and current_user.role != "superadmin":
        raise HTTPException(status_code=403, detail="System templates can only be removed by SuperAdmin")

    if panel.owner_id != current_user.id and current_user.role not in ["superadmin", "admin"]:
        raise HTTPException(status_code=403, detail="Permission denied")

    await db.delete(panel)
    await db.commit()
    return {"success": True, "message": "Panel deleted"}

@router.post("/{panel_id}/clone", response_model=PanelResponse)
async def clone_panel(
    panel_id: int,
    req: PanelCloneRequest,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """
    Administrator clone panel feature:
    Clones a panel and its widgets, and assigns ownership to target user or creates new template.
    """
    stmt = select(Panel).options(selectinload(Panel.widgets)).where(Panel.id == panel_id)
    res = await db.execute(stmt)
    source = res.scalars().first()
    if not source:
        raise HTTPException(status_code=404, detail="Source panel not found")

    target_owner = req.target_user_id or admin_user.id

    cloned_panel = Panel(
        name=req.new_panel_name,
        description=f"Cloned from {source.name}",
        owner_id=target_owner,
        is_default=False,
        is_system_template=False
    )
    db.add(cloned_panel)
    await db.flush()

    # Clone widgets
    for w in source.widgets:
        cloned_widget = Widget(
            panel_id=cloned_panel.id,
            type=w.type,
            title=w.title,
            is_system=w.is_system, # preserve system widget locking flag
            grid_col=w.grid_col,
            grid_row=w.grid_row,
            col_span=w.col_span,
            row_span=w.row_span,
            config=w.config
        )
        db.add(cloned_widget)

    await db.commit()
    
    # Reload with widgets
    reloaded_stmt = select(Panel).options(selectinload(Panel.widgets)).where(Panel.id == cloned_panel.id)
    r = await db.execute(reloaded_stmt)
    return r.scalars().first()

# Widget Operations
@router.post("/{panel_id}/widgets", response_model=WidgetResponse)
async def add_widget(
    panel_id: int,
    req: WidgetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Panel).where(Panel.id == panel_id)
    res = await db.execute(stmt)
    panel = res.scalars().first()
    if not panel:
        raise HTTPException(status_code=404, detail="Panel not found")

    if panel.owner_id != current_user.id and current_user.role not in ["superadmin", "admin"]:
        raise HTTPException(status_code=403, detail="Permission denied")

    # Only admin can create widgets marked is_system=True
    is_sys = req.is_system if current_user.role in ["superadmin", "admin"] else False

    new_widget = Widget(
        panel_id=panel_id,
        type=req.type,
        title=req.title,
        is_system=is_sys,
        grid_col=req.grid_col,
        grid_row=req.grid_row,
        col_span=req.col_span,
        row_span=req.row_span,
        config=req.config
    )
    db.add(new_widget)
    await db.commit()
    await db.refresh(new_widget)
    return new_widget

@router.put("/widgets/{widget_id}", response_model=WidgetResponse)
async def update_widget(
    widget_id: int,
    req: WidgetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Widget).where(Widget.id == widget_id)
    res = await db.execute(stmt)
    widget = res.scalars().first()
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")

    if req.title is not None:
        widget.title = req.title
    if req.grid_col is not None:
        widget.grid_col = req.grid_col
    if req.grid_row is not None:
        widget.grid_row = req.grid_row
    if req.col_span is not None:
        widget.col_span = req.col_span
    if req.row_span is not None:
        widget.row_span = req.row_span
    if req.config is not None:
        widget.config = req.config

    await db.commit()
    await db.refresh(widget)
    return widget

@router.delete("/widgets/{widget_id}")
async def delete_widget(
    widget_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Widget).where(Widget.id == widget_id)
    res = await db.execute(stmt)
    widget = res.scalars().first()
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")

    # Critical requirement: System widgets cannot be deleted by standard users
    if widget.is_system and current_user.role not in ["superadmin", "admin"]:
        raise HTTPException(status_code=403, detail="System widgets are locked and cannot be deleted by users")

    await db.delete(widget)
    await db.commit()
    return {"success": True, "message": "Widget removed"}
