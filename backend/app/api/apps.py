from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.integration import AppBookmark
from app.models.user import User
from app.schemas.integration import (
    AppBookmarkCreate, AppBookmarkUpdate, AppBookmarkResponse
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/apps", tags=["apps"])

@router.get("", response_model=List[AppBookmarkResponse])
async def list_apps(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(AppBookmark).where(AppBookmark.is_active == True).order_by(AppBookmark.display_order.asc(), AppBookmark.id.asc())
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("", response_model=AppBookmarkResponse)
async def create_app(
    req: AppBookmarkCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not (current_user.can_manage_apps or current_user.role in ["superadmin", "admin"]):
        raise HTTPException(status_code=403, detail="Permission to manage applications denied")

    app_item = AppBookmark(
        title=req.title,
        description=req.description,
        url=req.url,
        icon=req.icon or "terminal",
        color=req.color or "#00f3ff",
        target=req.target or "_blank",
        display_order=req.display_order or 0,
        group_name=req.group_name or "Основное",
        is_active=True
    )
    db.add(app_item)
    await db.commit()
    await db.refresh(app_item)
    return app_item

@router.put("/{app_id}", response_model=AppBookmarkResponse)
async def update_app(
    app_id: int,
    req: AppBookmarkUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not (current_user.can_manage_apps or current_user.role in ["superadmin", "admin"]):
        raise HTTPException(status_code=403, detail="Permission to manage applications denied")

    stmt = select(AppBookmark).where(AppBookmark.id == app_id)
    res = await db.execute(stmt)
    app_item = res.scalars().first()
    if not app_item:
        raise HTTPException(status_code=404, detail="App bookmark not found")

    if req.title is not None:
        app_item.title = req.title
    if req.description is not None:
        app_item.description = req.description
    if req.url is not None:
        app_item.url = req.url
    if req.icon is not None:
        app_item.icon = req.icon
    if req.color is not None:
        app_item.color = req.color
    if req.target is not None:
        app_item.target = req.target
    if req.display_order is not None:
        app_item.display_order = req.display_order
    if req.group_name is not None:
        app_item.group_name = req.group_name
    if req.is_active is not None:
        app_item.is_active = req.is_active

    await db.commit()
    await db.refresh(app_item)
    return app_item

@router.delete("/{app_id}")
async def delete_app(
    app_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not (current_user.can_manage_apps or current_user.role in ["superadmin", "admin"]):
        raise HTTPException(status_code=403, detail="Permission denied")

    stmt = select(AppBookmark).where(AppBookmark.id == app_id)
    res = await db.execute(stmt)
    app_item = res.scalars().first()
    if not app_item:
        raise HTTPException(status_code=404, detail="App bookmark not found")

    await db.delete(app_item)
    await db.commit()
    return {"success": True, "message": "App bookmark removed"}
