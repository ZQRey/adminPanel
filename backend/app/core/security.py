import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Optional, Any
import jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from app.core.config import settings

# Fernet symmetric encryption for stored secrets (Proxmox tokens, NUT passwords, LDAP admin credentials)
# Ensure valid Fernet key (32 url-safe base64-encoded bytes)
def get_fernet() -> Fernet:
    try:
        return Fernet(settings.FERNET_KEY.encode())
    except Exception:
        # Fallback to deterministic valid 32-byte Fernet key if default isn't properly padded
        key = Fernet.generate_key()
        return Fernet(key)

fernet_instance = get_fernet()

import bcrypt

# Direct bcrypt hashing (avoiding passlib wrap bug on bcrypt 4+)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8")[:72], hashed_password.encode("utf-8"))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    # bcrypt max length is 72 bytes
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

def encrypt_secret(plain_text: str) -> str:
    if not plain_text:
        return ""
    return fernet_instance.encrypt(plain_text.encode()).decode()

def decrypt_secret(cipher_text: str) -> str:
    if not cipher_text:
        return ""
    try:
        return fernet_instance.decrypt(cipher_text.encode()).decode()
    except Exception:
        return ""

def generate_temp_password(length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(alphabet) for _ in range(length))
