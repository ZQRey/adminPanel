import asyncio
import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from app.core.config import settings
from app.core.database import engine, Base, AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.panel import Panel, Widget
from app.models.integration import AppBookmark, Integration
from app.services.telemetry_hub import telemetry_hub
from app.api import auth, users, panels, integrations, apps, plugins, ws

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("cyber_hud")

async def init_db_and_seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Check if SuperAdmin exists
        user_stmt = select(User).where(User.username == "admin")
        res = await session.execute(user_stmt)
        admin = res.scalars().first()
        if not admin:
            logger.info("Seeding initial SuperAdmin account (admin / admin123)...")
            admin = User(
                username="admin",
                hashed_password=get_password_hash("admin123"),
                role="superadmin",
                auth_source="local",
                can_manage_integrations=True,
                can_manage_apps=True,
                can_manage_panels=True,
                must_change_password=False,
                is_active=True
            )
            session.add(admin)
            await session.commit()
            await session.refresh(admin)

        # Check if default system panel exists
        panel_stmt = select(Panel).where(Panel.is_system_template == True)
        p_res = await session.execute(panel_stmt)
        default_panel = p_res.scalars().first()
        if not default_panel:
            logger.info("Seeding default HUD Sci-Fi system panel and widgets...")
            default_panel = Panel(
                name="Cyber Primary HUD",
                description="Default High-Tech Sci-Fi Operations Center",
                owner_id=admin.id,
                is_default=True,
                is_system_template=True
            )
            session.add(default_panel)
            await session.flush()

            # Seed widgets
            widgets = [
                Widget(
                    panel_id=default_panel.id,
                    type="clock",
                    title="CHRONO & TELEMETRY",
                    is_system=True, # System widget, non-deletable
                    grid_col=1,
                    grid_row=1,
                    col_span=1,
                    row_span=1,
                    config=json.dumps({"format": "24h", "show_seconds": True, "show_uptime": True})
                ),
                Widget(
                    panel_id=default_panel.id,
                    type="weather",
                    title="ATMOSPHERIC SENSORS",
                    is_system=True,
                    grid_col=1,
                    grid_row=2,
                    col_span=1,
                    row_span=1,
                    config=json.dumps({"city": "Neo-Tokyo", "units": "metric"})
                ),
                Widget(
                    panel_id=default_panel.id,
                    type="proxmox",
                    title="PROXMOX VE HYPERVISOR",
                    is_system=True,
                    grid_col=3,
                    grid_row=1,
                    col_span=1,
                    row_span=1,
                    config=json.dumps({"refresh_sec": 2})
                ),
                Widget(
                    panel_id=default_panel.id,
                    type="nut",
                    title="NUT UPS POWER CELL",
                    is_system=True,
                    grid_col=3,
                    grid_row=2,
                    col_span=1,
                    row_span=1,
                    config=json.dumps({"ups_name": "ups"})
                ),
                Widget(
                    panel_id=default_panel.id,
                    type="plugin",
                    title="QUANTUM MESH MONITOR",
                    is_system=False,
                    grid_col=2,
                    grid_row=3,
                    col_span=1,
                    row_span=1,
                    config=json.dumps({"plugin_name": "System Telemetry"})
                )
            ]
            session.add_all(widgets)
            await session.commit()

        # Seed default bookmarks (apps for radial menu)
        apps_stmt = select(AppBookmark)
        a_res = await session.execute(apps_stmt)
        if not a_res.scalars().first():
            logger.info("Seeding default smart bookmark applications for radial menu...")
            apps = [
                AppBookmark(
                    title="Proxmox Node",
                    description="Hypervisor Web GUI",
                    url="https://proxmox.local:8006",
                    icon="server",
                    color="#00f3ff",
                    target="_blank",
                    display_order=1
                ),
                AppBookmark(
                    title="Grafana HUD",
                    description="Telemetry Metrics Dashboards",
                    url="http://grafana.local:3000",
                    icon="activity",
                    color="#00ff66",
                    target="_blank",
                    display_order=2
                ),
                AppBookmark(
                    title="Vaultwarden",
                    description="Encrypted Vault",
                    url="https://vault.local",
                    icon="shield",
                    color="#ffaa00",
                    target="_blank",
                    display_order=3
                ),
                AppBookmark(
                    title="Portainer Core",
                    description="Container Cluster Management",
                    url="https://portainer.local:9443",
                    icon="box",
                    color="#00f3ff",
                    target="_blank",
                    display_order=4
                )
            ]
            session.add_all(apps)
            await session.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Sci-Fi HUD API Server...")
    await init_db_and_seed()
    await telemetry_hub.start_broadcasting()
    yield
    # Shutdown
    logger.info("Shutting down Sci-Fi HUD API Server...")
    await telemetry_hub.stop_broadcasting()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(panels.router, prefix="/api")
app.include_router(integrations.router, prefix="/api")
app.include_router(apps.router, prefix="/api")
app.include_router(plugins.router, prefix="/api")
app.include_router(ws.router)

# Mount static files
app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")

@app.get("/api/health")
async def health_check():
    return {"status": "operational", "version": settings.VERSION}
