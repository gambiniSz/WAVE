import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db  # garante que o .env já foi carregado
from models import Pescador

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise ValueError("JWT_SECRET não foi encontrada no arquivo .env")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


def hash_senha(senha: str) -> str:
    # bcrypt só considera os 72 primeiros bytes
    return bcrypt.hashpw(senha.encode()[:72], bcrypt.gensalt()).decode()


def verificar_senha(senha: str, senha_hash: str | None) -> bool:
    if not senha_hash:
        return False
    try:
        return bcrypt.checkpw(senha.encode()[:72], senha_hash.encode())
    except ValueError:
        return False


def criar_token(id_pescador: int) -> str:
    agora = datetime.now(timezone.utc)
    payload = {
        "sub": str(id_pescador),
        "iat": agora,
        "exp": agora + timedelta(minutes=JWT_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> Pescador:
    erro = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        id_pescador = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise erro
    pescador = await db.get(Pescador, id_pescador)
    if not pescador:
        raise erro
    return pescador
