import asyncio
import sys
from app.main import init_db_and_seed
from app.core.database import AsyncSessionLocal
from app.services.auth_service import authenticate_user
from app.services.plugin_runner import PluginRunner
from app.services.telemetry_hub import telemetry_hub
from app.core.security import encrypt_secret, decrypt_secret

async def test_backend():
    print("[1] Initializing DB and seeding...")
    await init_db_and_seed()
    print("    DB initialized and seeded successfully.")

    print("[2] Testing Authentication Service...")
    async with AsyncSessionLocal() as session:
        user, auth_source = await authenticate_user(session, "admin", "admin123")
        assert user is not None, "Admin user authentication failed"
        assert user.username == "admin", f"Expected admin, got {user.username}"
        assert user.role == "superadmin", f"Expected superadmin, got {user.role}"
        print(f"    Admin login OK (auth_source={auth_source}, role={user.role})")

        # Test invalid login (triggers 401 on API)
        bad_user, reason = await authenticate_user(session, "admin", "wrong_password")
        assert bad_user is None, "Bad login should fail"
        print(f"    Invalid credentials correctly rejected (reason={reason})")

    print("[3] Testing Credentials Encryption (Fernet)...")
    secret = "SuperSecretProxmoxToken123!@#"
    encrypted = encrypt_secret(secret)
    decrypted = decrypt_secret(encrypted)
    assert decrypted == secret, "Encryption/Decryption mismatch"
    assert encrypted != secret, "Encryption failed to disguise secret"
    print("    Fernet symmetric encryption/decryption OK.")

    print("[4] Testing Isolated Python Plugin Runner...")
    res = await PluginRunner.execute_plugin("system_telemetry.py", timeout_seconds=4.0)
    assert res.get("success") is True, f"Plugin run failed: {res}"
    metrics = res.get("metrics", {})
    assert "platform" in metrics, f"Platform not in metrics: {metrics}"
    print(f"    Plugin execution OK. Platform: {metrics.get('platform')}, Entropy: {metrics.get('quantum_entropy')}%")

    print("[5] Testing Telemetry Hub packet generation...")
    packet = await telemetry_hub.generate_telemetry_packet()
    assert packet.get("type") == "telemetry_update"
    assert "proxmox" in packet["data"]
    assert "nut" in packet["data"]
    print("    Telemetry packet generated successfully.")

    print("\nALL BACKEND VERIFICATION CHECKS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(test_backend())
