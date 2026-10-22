import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

import models  # noqa: F401  (registra as tabelas no Base antes do create_all)
from auth_routes import router as auth_router
from chatbot_routes import router as chatbot_router
from clima_routes import router as clima_router
from database import Base, engine
from equipamento_routes import router as equipamento_router
from local_routes import router as local_router
from pescador_routes import router as pescador_router
from venda_routes import router as venda_router
from vinculo_routes import router as vinculo_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # create_all só cria tabelas novas; alterações em tabelas existentes
    # devem ser aplicadas com a migração em migrations/
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="Wave API", version="1.0.0", lifespan=lifespan)

origens = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origens,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=409,
        content={"detail": "Operação viola uma restrição do banco (registro duplicado ou referência inválida)"},
    )


app.include_router(auth_router)
app.include_router(pescador_router)
app.include_router(vinculo_router)
app.include_router(local_router)
app.include_router(venda_router)
app.include_router(equipamento_router)
app.include_router(clima_router)
app.include_router(chatbot_router)


@app.get("/")
async def read_root():
    return {"message": "API rodando e conectada com sucesso!"}


@app.get("/health")
async def health():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        return JSONResponse(status_code=503, content={"status": "erro", "banco": "indisponível"})
    return {"status": "ok", "banco": "ok"}
