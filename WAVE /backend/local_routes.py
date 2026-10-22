from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db
from models import LocalPesca
from schemas import LocalPescaCreate, LocalPescaResponse

router = APIRouter(prefix="/api/locais", tags=["Locais de Pesca"])


@router.post("/", response_model=LocalPescaResponse, status_code=status.HTTP_201_CREATED)
async def criar(local: LocalPescaCreate, db: AsyncSession = Depends(get_db)):
    db_local = LocalPesca(**local.model_dump())
    db.add(db_local)
    await db.commit()
    await db.refresh(db_local)
    return db_local


@router.get("/", response_model=List[LocalPescaResponse])
async def listar(db: AsyncSession = Depends(get_db)):
    resultado = await db.execute(select(LocalPesca).order_by(LocalPesca.id_local))
    return resultado.scalars().all()


@router.get("/{id_local}", response_model=LocalPescaResponse)
async def buscar(id_local: int, db: AsyncSession = Depends(get_db)):
    local = await db.get(LocalPesca, id_local)
    if not local:
        raise HTTPException(status_code=404, detail="Local não encontrado")
    return local


@router.put("/{id_local}", response_model=LocalPescaResponse)
async def atualizar(id_local: int, dados: LocalPescaCreate, db: AsyncSession = Depends(get_db)):
    local = await db.get(LocalPesca, id_local)
    if not local:
        raise HTTPException(status_code=404, detail="Local não encontrado")
    for chave, valor in dados.model_dump().items():
        setattr(local, chave, valor)
    await db.commit()
    await db.refresh(local)
    return local


@router.delete("/{id_local}")
async def deletar(id_local: int, db: AsyncSession = Depends(get_db)):
    resultado = await db.execute(
        select(LocalPesca)
        .options(selectinload(LocalPesca.climas), selectinload(LocalPesca.pescadores))
        .where(LocalPesca.id_local == id_local)
    )
    local = resultado.scalar_one_or_none()
    if not local:
        raise HTTPException(status_code=404, detail="Local não encontrado")
    await db.delete(local)
    await db.commit()
    return {"message": "Local removido com sucesso"}
