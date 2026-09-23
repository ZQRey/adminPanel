import json
import logging
from typing import Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ldap3 import Server, Connection, ALL, NTLM
from app.models.user import User
from app.models.integration import Integration
from app.core.security import verify_password, decrypt_secret

logger = logging.getLogger(__name__)

async def authenticate_user(db: AsyncSession, username: str, password: str) -> Tuple[Optional[User], str]:
    """
    Authenticates a user with AD LDAP priority and local DB fallback.
    Returns (User, auth_method) or (None, failure_reason).
    """
    # 1. Attempt AD LDAP if configured and active
    stmt = select(Integration).where(Integration.type == "ad_ldap", Integration.is_enabled == True)
    result = await db.execute(stmt)
    ad_integration = result.scalars().first()

    if ad_integration and ad_integration.encrypted_payload:
        try:
            config_str = decrypt_secret(ad_integration.encrypted_payload)
            config = json.loads(config_str) if config_str else {}
            
            host = ad_integration.host
            port = ad_integration.port or (636 if config.get("use_ssl") else 389)
            base_dn = config.get("base_dn", "")
            use_ssl = config.get("use_ssl", False)
            admin_dn = config.get("admin_dn")
            admin_pass = config.get("admin_password")

            server = Server(host, port=port, use_ssl=use_ssl, get_info=ALL, connect_timeout=3)
            
            user_principal = username
            if "@" not in username and base_dn:
                # Construct domain principal if domain parts exist
                domain_parts = [p.split("=")[1] for p in base_dn.split(",") if p.lower().startswith("dc=")]
                if domain_parts:
                    user_principal = f"{username}@{'.'.join(domain_parts)}"

            # Direct bind attempt with user credentials
            conn = Connection(server, user=user_principal, password=password, auto_bind=False)
            if conn.bind():
                conn.unbind()
                logger.info(f"AD LDAP authentication succeeded for user: {username}")
                
                # Check if user already exists locally, otherwise provision automatically
                user_stmt = select(User).where(User.username == username)
                u_res = await db.execute(user_stmt)
                user = u_res.scalars().first()
                
                if not user:
                    # Auto-provision AD user
                    user = User(
                        username=username,
                        hashed_password=None,
                        role="user",
                        auth_source="ad",
                        can_manage_integrations=False,
                        can_manage_apps=False,
                        can_manage_panels=True,
                        must_change_password=False,
                        is_active=True
                    )
                    db.add(user)
                    await db.commit()
                    await db.refresh(user)
                return user, "ad_ldap"
            else:
                logger.warning(f"AD LDAP bind failed for user: {username}: {conn.result}")
        except Exception as e:
            logger.warning(f"AD LDAP exception occurred during auth for {username}: {e}. Falling back to local DB.")

    # 2. Fallback to Local SQLite DB
    user_stmt = select(User).where(User.username == username)
    u_res = await db.execute(user_stmt)
    local_user = u_res.scalars().first()

    if not local_user:
        return None, "user_not_found"

    if not local_user.is_active:
        return None, "user_inactive"

    if not local_user.hashed_password:
        return None, "ad_only_user"

    if not verify_password(password, local_user.hashed_password):
        return None, "invalid_credentials"

    return local_user, "local"
