from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import clima_service
from database import get_db
from models import Clima, LocalPesca
from pagination import Paginacao
from schemas import ClimaCreate, ClimaResponse
from security import get_current_user

router = APIRouter(prefix="/api/clima", tags=["Clima"], dependencies=[Depends(get_current_user)])


async def _garantir_local(db: AsyncSession, id_local: int) -> LocalPesca:
    local = await db.get(LocalPesca, id_local)
    if not local:
        raise HTTPException(status_code=404, detail="Local não encontrado")
    return local


@router.post("/", response_model=ClimaResponse, status_code=status.HTTP_201_CREATED)
async def criar(clima: ClimaCreate, db: AsyncSession = Depends(get_db)):
    await _garantir_local(db, clima.id_local)
    db_clima = Clima(**clima.model_dump())
    db.add(db_clima)
    await db.commit()
    await db.refresh(db_clima)
    return db_clima


@router.get("/", response_model=List[ClimaResponse])
async def listar(
    id_local: Optional[int] = None,
    p: Paginacao = Depends(),
    db: AsyncSession = Depends(get_db),
):
    consulta = select(Clima).order_by(Clima.data_registro.desc(), Clima.id_clima.desc())
    if id_local is not None:
        consulta = consulta.where(Clima.id_local == id_local)
    resultado = await db.execute(consulta.offset(p.skip).limit(p.limit))
    return resultado.scalars().all()


@router.get("/local/{id_local}/atual", response_model=ClimaResponse)
async def clima_atual(id_local: int, db: AsyncSession = Depends(get_db)):
    resultado = await db.execute(
        select(Clima)
        .where(Clima.id_local == id_local)
        .order_by(Clima.data_registro.desc(), Clima.id_clima.desc())
        .limit(1)
    )
    clima = resultado.scalar_one_or_none()
    if not clima:
        raise HTTPException(status_code=404, detail="Sem registro de clima para este local")
    return clima


@router.post("/local/{id_local}/sincronizar", response_model=ClimaResponse)
async def sincronizar(id_local: int, db: AsyncSession = Depends(get_db)):
    """Busca o clima real (Open-Meteo) pelas coordenadas do local e grava o registro de hoje."""
    local = await _garantir_local(db, id_local)
    try:
        dados = await clima_service.buscar_clima_atual(local.latitude, local.longitude)
    except clima_service.ClimaIndisponivel as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    hoje = date.today()
    resultado = await db.execute(
        select(Clima)
        .where(Clima.id_local == id_local, Clima.data_registro == hoje)
        .order_by(Clima.id_clima.desc())
        .limit(1)
    )
    clima = resultado.scalar_one_or_none()
    if clima:  # um registro por local por dia: atualiza em vez de duplicar
        for chave, valor in dados.items():
            setattr(clima, chave, valor)
    else:
        clima = Clima(id_local=id_local, data_registro=hoje, **dados)
        db.add(clima)
    await db.commit()
    await db.refresh(clima)
    return clima


@router.get("/{id_clima}", response_model=ClimaResponse)
async def buscar(id_clima: int, db: AsyncSession = Depends(get_db)):
    clima = await db.get(Clima, id_clima)
    if not clima:
        raise HTTPException(status_code=404, detail="Registro de clima não encontrado")
    return clima


@router.put("/{id_clima}", response_model=ClimaResponse)
async def atualizar(id_clima: int, dados: ClimaCreate, db: AsyncSession = Depends(get_db)):
    clima = await db.get(Clima, id_clima)
    if not clima:
        raise HTTPException(status_code=404, detail="Registro de clima não encontrado")
    await _garantir_local(db, dados.id_local)
    for chave, valor in dados.model_dump().items():
        setattr(clima, chave, valor)
    await db.commit()
    await db.refresh(clima)
    return clima


@router.delete("/{id_clima}")
async def deletar(id_clima: int, db: AsyncSession = Depends(get_db)):
    clima = await db.get(Clima, id_clima)
    if not clima:
        raise HTTPException(status_code=404, detail="Registro de clima não encontrado")
    await db.delete(clima)
    await db.commit()
    return {"message": "Registro de clima removido com sucesso"}
