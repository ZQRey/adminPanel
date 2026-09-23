from typing import Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from app.services.plugin_runner import PluginRunner
from app.api.deps import require_admin
from app.models.user import User

router = APIRouter(prefix="/plugins", tags=["plugins"])

class PluginSaveRequest(BaseModel):
    filename: str
    code: str

@router.get("")
async def list_plugins(admin_user: User = Depends(require_admin)):
    return PluginRunner.list_plugins()

@router.get("/{filename}")
async def get_plugin(filename: str, admin_user: User = Depends(require_admin)):
    try:
        code = PluginRunner.get_plugin_code(filename)
        return {"filename": filename, "code": code}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Plugin file not found")

@router.post("")
async def save_plugin(req: PluginSaveRequest, admin_user: User = Depends(require_admin)):
    try:
        PluginRunner.save_plugin_code(req.filename, req.code)
        return {"success": True, "message": f"Plugin {req.filename} saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{filename}")
async def delete_plugin(filename: str, admin_user: User = Depends(require_admin)):
    success = PluginRunner.delete_plugin(filename)
    if not success:
        raise HTTPException(status_code=404, detail="Plugin file not found")
    return {"success": True, "message": f"Plugin {filename} deleted"}

@router.post("/{filename}/run")
async def run_plugin(filename: str, admin_user: User = Depends(require_admin)):
    result = await PluginRunner.execute_plugin(filename)
    return result
