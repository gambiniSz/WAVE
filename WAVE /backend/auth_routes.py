from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

import pescador_controller
from database import get_db
from schemas import LoginRequest, PescadorCreate, PescadorResponse, Token
from security import criar_token

router = APIRouter(prefix="/api/auth", tags=["Autenticação"])

_CREDENCIAIS_INVALIDAS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="E-mail ou senha incorretos",
    headers={"WWW-Authenticate": "Bearer"},
)


@router.post("/registro", response_model=PescadorResponse, status_code=status.HTTP_201_CREATED)
async def registro(dados: PescadorCreate, db: AsyncSession = Depends(get_db)):
    return await pescador_controller.criar_pescador(db, dados)


@router.post("/login", response_model=Token)
async def login(dados: LoginRequest, db: AsyncSession = Depends(get_db)):
    pescador = await pescador_controller.autenticar(db, dados.email, dados.senha)
    if not pescador:
        raise _CREDENCIAIS_INVALIDAS
    return Token(access_token=criar_token(pescador.id_pescador))


@router.post("/token", response_model=Token, include_in_schema=True)
async def token_form(
    form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """Mesmo login, em formato de formulário (usado pelo botão Authorize do /docs)."""
    pescador = await pescador_controller.autenticar(db, form.username, form.password)
    if not pescador:
        raise _CREDENCIAIS_INVALIDAS
    return Token(access_token=criar_token(pescador.id_pescador))
