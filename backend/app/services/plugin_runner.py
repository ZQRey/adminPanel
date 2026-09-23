import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, List
from app.core.config import settings

logger = logging.getLogger(__name__)

class PluginRunner:
    @staticmethod
    def list_plugins() -> List[Dict[str, Any]]:
        plugins = []
        plugins_dir = settings.PLUGINS_DIR
        for item in plugins_dir.glob("*.py"):
            if item.name.startswith("__"):
                continue
            stat = item.stat()
            plugins.append({
                "filename": item.name,
                "name": item.stem.replace("_", " ").title(),
                "path": str(item),
                "size_bytes": stat.st_size,
                "modified": stat.st_mtime
            })
        return plugins

    @staticmethod
    def get_plugin_code(filename: str) -> str:
        safe_name = Path(filename).name
        target = settings.PLUGINS_DIR / safe_name
        if not target.exists() or not target.is_file():
            raise FileNotFoundError("Plugin file not found")
        return target.read_text(encoding="utf-8")

    @staticmethod
    def save_plugin_code(filename: str, code: str) -> None:
        safe_name = Path(filename).name
        if not safe_name.endswith(".py"):
            safe_name += ".py"
        target = settings.PLUGINS_DIR / safe_name
        target.write_text(code, encoding="utf-8")

    @staticmethod
    def delete_plugin(filename: str) -> bool:
        safe_name = Path(filename).name
        target = settings.PLUGINS_DIR / safe_name
        if target.exists() and target.is_file():
            target.unlink()
            return True
        return False

    @staticmethod
    async def execute_plugin(filename: str, timeout_seconds: float = 4.0) -> Dict[str, Any]:
        """
        Executes a Python plugin script in an isolated subprocess with strict timeout.
        """
        safe_name = Path(filename).name
        script_path = settings.PLUGINS_DIR / safe_name
        if not script_path.exists():
            return {"error": "Plugin file not found", "success": False}

        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        # Restrict environment to avoid passing app secrets to custom plugin scripts
        env.pop("SECRET_KEY", None)
        env.pop("FERNET_KEY", None)

        try:
            process = await asyncio.create_subprocess_exec(
                sys.executable,
                str(script_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
                cwd=str(settings.PLUGINS_DIR)
            )

            try:
                stdout_data, stderr_data = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout_seconds
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return {
                    "success": False,
                    "error": f"Execution timed out (> {timeout_seconds}s)",
                    "plugin": safe_name
                }

            stdout_str = stdout_data.decode("utf-8", errors="replace").strip()
            stderr_str = stderr_data.decode("utf-8", errors="replace").strip()

            parsed_metrics = None
            if stdout_str:
                try:
                    parsed_metrics = json.loads(stdout_str)
                except Exception:
                    parsed_metrics = {"raw_output": stdout_str}

            return {
                "success": process.returncode == 0,
                "exit_code": process.returncode,
                "metrics": parsed_metrics,
                "stderr": stderr_str if stderr_str else None,
                "plugin": safe_name
            }

        except Exception as e:
            logger.error(f"Plugin execution failure for {safe_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "plugin": safe_name
            }

    @classmethod
    async def collect_all_metrics(cls) -> Dict[str, Any]:
        """Collects metrics from all available plugins concurrently."""
        plugins = cls.list_plugins()
        tasks = [cls.execute_plugin(p["filename"]) for p in plugins]
        if not tasks:
            return {}
        results = await asyncio.gather(*tasks, return_exceptions=True)
        aggregated = {}
        for p, r in zip(plugins, results):
            if isinstance(r, dict) and r.get("success"):
                aggregated[p["name"]] = r.get("metrics")
        return aggregated
