import asyncio
import json
import logging
import time
from typing import Set
from fastapi import WebSocket
from app.services.proxy_service import ProxyService
from app.services.plugin_runner import PluginRunner

logger = logging.getLogger(__name__)

class TelemetryHub:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self._broadcast_task: asyncio.Task = None
        self._is_running: bool = False

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")
        
        # Send immediate initial burst packet
        initial_packet = await self.generate_telemetry_packet()
        await websocket.send_text(json.dumps(initial_packet))

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket client disconnected. Total clients: {len(self.active_connections)}")

    async def generate_telemetry_packet(self) -> dict:
        # Collect telemetry concurrently
        proxmox_coro = ProxyService.fetch_proxmox_metrics("127.0.0.1", 8006, {})
        nut_coro = ProxyService.fetch_nut_metrics("127.0.0.1", 3493, {})
        plugins_coro = PluginRunner.collect_all_metrics()

        proxmox_data, nut_data, plugins_data = await asyncio.gather(
            proxmox_coro, nut_coro, plugins_coro, return_exceptions=True
        )

        return {
            "type": "telemetry_update",
            "timestamp": time.time(),
            "iso_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "data": {
                "proxmox": proxmox_data if isinstance(proxmox_data, dict) else {"error": str(proxmox_data)},
                "nut": nut_data if isinstance(nut_data, dict) else {"error": str(nut_data)},
                "plugins": plugins_data if isinstance(plugins_data, dict) else {}
            }
        }

    async def start_broadcasting(self):
        if self._is_running:
            return
        self._is_running = True
        self._broadcast_task = asyncio.create_task(self._broadcast_loop())

    async def stop_broadcasting(self):
        self._is_running = False
        if self._broadcast_task:
            self._broadcast_task.cancel()

    async def _broadcast_loop(self):
        while self._is_running:
            try:
                await asyncio.sleep(2.0)
                if not self.active_connections:
                    continue

                packet = await self.generate_telemetry_packet()
                payload = json.dumps(packet)

                # Send to all connected clients
                disconnected = []
                for ws in list(self.active_connections):
                    try:
                        await ws.send_text(payload)
                    except Exception:
                        disconnected.append(ws)

                for ws in disconnected:
                    self.active_connections.discard(ws)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in telemetry broadcast loop: {e}")
                await asyncio.sleep(2.0)

telemetry_hub = TelemetryHub()
