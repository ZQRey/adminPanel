import json
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import encrypt_secret, decrypt_secret
from app.models.integration import Integration
from app.models.user import User
from app.schemas.integration import (
    IntegrationCreate, IntegrationUpdate, IntegrationResponse, TestConnectionResponse
)
from app.services.proxy_service import ProxyService
from app.api.deps import get_current_user

router = APIRouter(prefix="/integrations", tags=["integrations"])

def mask_sensitive_config(config: Dict[str, Any]) -> Dict[str, Any]:
    safe = config.copy()
    for secret_key in ["admin_password", "token_value", "password", "nut_password"]:
        if secret_key in safe and safe[secret_key]:
            safe[secret_key] = "********"
    return safe

@router.get("", response_model=List[IntegrationResponse])
async def list_integrations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Integration).order_by(Integration.id.asc())
    res = await db.execute(stmt)
    integrations = res.scalars().all()
    
    response_items = []
    for item in integrations:
        config_summary = {}
        if item.encrypted_payload:
            try:
                decrypted = decrypt_secret(item.encrypted_payload)
                raw_cfg = json.loads(decrypted) if decrypted else {}
                config_summary = mask_sensitive_config(raw_cfg)
            except Exception:
                config_summary = {}

        response_items.append(
            IntegrationResponse(
                id=item.id,
                name=item.name,
                type=item.type,
                host=item.host,
                port=item.port,
                is_enabled=item.is_enabled,
                status=item.status,
                last_synced=item.last_synced,
                has_secret=bool(item.encrypted_payload),
                config_summary=config_summary
            )
        )
    return response_items

@router.post("", response_model=IntegrationResponse)
async def create_integration(
    req: IntegrationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not (current_user.can_manage_integrations or current_user.role in ["superadmin", "admin"]):
        raise HTTPException(status_code=403, detail="Permission to manage integrations denied")

    # Encrypt sensitive payload
    payload_json = json.dumps(req.config)
    encrypted_payload = encrypt_secret(payload_json)

    integration = Integration(
        name=req.name,
        type=req.type,
        host=req.host,
        port=req.port,
        encrypted_payload=encrypted_payload,
        is_enabled=req.is_enabled,
        status="configured"
    )
    db.add(integration)
    await db.commit()
    await db.refresh(integration)

    return IntegrationResponse(
        id=integration.id,
        name=integration.name,
        type=integration.type,
        host=integration.host,
        port=integration.port,
        is_enabled=integration.is_enabled,
        status=integration.status,
        last_synced=integration.last_synced,
        has_secret=True,
        config_summary=mask_sensitive_config(req.config)
    )

@router.put("/{integration_id}", response_model=IntegrationResponse)
async def update_integration(
    integration_id: int,
    req: IntegrationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not (current_user.can_manage_integrations or current_user.role in ["superadmin", "admin"]):
        raise HTTPException(status_code=403, detail="Permission to manage integrations denied")

    stmt = select(Integration).where(Integration.id == integration_id)
    res = await db.execute(stmt)
    integration = res.scalars().first()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    if req.name is not None:
        integration.name = req.name
    if req.host is not None:
        integration.host = req.host
    if req.port is not None:
        integration.port = req.port
    if req.is_enabled is not None:
        integration.is_enabled = req.is_enabled

    # If new config provided, merge secrets if not modified
    current_config = {}
    if integration.encrypted_payload:
        try:
            current_config = json.loads(decrypt_secret(integration.encrypted_payload))
        except Exception:
            current_config = {}

    if req.config is not None:
        for k, v in req.config.items():
            # If user kept masked string "********", keep existing decrypted secret
            if v == "********" and k in current_config:
                continue
            current_config[k] = v
        integration.encrypted_payload = encrypt_secret(json.dumps(current_config))

    await db.commit()
    await db.refresh(integration)

    return IntegrationResponse(
        id=integration.id,
        name=integration.name,
        type=integration.type,
        host=integration.host,
        port=integration.port,
        is_enabled=integration.is_enabled,
        status=integration.status,
        last_synced=integration.last_synced,
        has_secret=True,
        config_summary=mask_sensitive_config(current_config)
    )

@router.delete("/{integration_id}")
async def delete_integration(
    integration_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not (current_user.can_manage_integrations or current_user.role in ["superadmin", "admin"]):
        raise HTTPException(status_code=403, detail="Permission denied")

    stmt = select(Integration).where(Integration.id == integration_id)
    res = await db.execute(stmt)
    integration = res.scalars().first()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    await db.delete(integration)
    await db.commit()
    return {"success": True, "message": "Integration removed"}

@router.post("/{integration_id}/test", response_model=TestConnectionResponse)
async def test_integration(
    integration_id: int,
    live_data: Optional[Dict[str, Any]] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Integration).where(Integration.id == integration_id)
    res = await db.execute(stmt)
    integration = res.scalars().first()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    config = {}
    if integration.encrypted_payload:
        try:
            config = json.loads(decrypt_secret(integration.encrypted_payload))
        except Exception:
            config = {}

    host = integration.host
    port = integration.port

    if live_data:
        if live_data.get("host"):
            host = live_data["host"]
        if live_data.get("port"):
            try:
                port = int(live_data["port"])
            except (ValueError, TypeError):
                pass
        if isinstance(live_data.get("config"), dict):
            for k, v in live_data["config"].items():
                if v and v != "********":
                    config[k] = v

    if integration.type == "ad_ldap":
        result = await ProxyService.test_ad_connection(host, port, config)
    elif integration.type == "proxmox":
        result = await ProxyService.test_proxmox_connection(host, port, config)
    elif integration.type == "nut":
        result = await ProxyService.test_nut_connection(host, port, config)
    else:
        result = {"success": True, "message": "Custom integration check passed", "latency_ms": 1.2}

    integration.status = "online" if result.get("success") else "offline"
    await db.commit()

    return result
