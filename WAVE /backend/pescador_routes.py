from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import pescador_controller
from database import get_db
from schemas import PescadorCreate, PescadorResponse

router = APIRouter(prefix="/api/pescadores", tags=["Pescadores"])


@router.post("/", response_model=PescadorResponse, status_code=status.HTTP_201_CREATED)
async def criar(pescador: PescadorCreate, db: AsyncSession = Depends(get_db)):
    return await pescador_controller.criar_pescador(db, pescador)


@router.get("/", response_model=List[PescadorResponse])
async def listar(db: AsyncSession = Depends(get_db)):
    return await pescador_controller.listar_pescadores(db)


@router.get("/{id_pescador}", response_model=PescadorResponse)
async def buscar_por_id(id_pescador: int, db: AsyncSession = Depends(get_db)):
    pescador = await pescador_controller.buscar_pescador_por_id(db, id_pescador)
    if not pescador:
        raise HTTPException(status_code=404, detail="Pescador não encontrado")
    return pescador


@router.put("/{id_pescador}", response_model=PescadorResponse)
async def atualizar(id_pescador: int, dados: PescadorCreate, db: AsyncSession = Depends(get_db)):
    pescador = await pescador_controller.atualizar_pescador(db, id_pescador, dados)
    if not pescador:
        raise HTTPException(status_code=404, detail="Pescador não encontrado")
    return pescador


@router.delete("/{id_pescador}", status_code=status.HTTP_200_OK)
async def deletar(id_pescador: int, db: AsyncSession = Depends(get_db)):
    if not await pescador_controller.deletar_pescador(db, id_pescador):
        raise HTTPException(status_code=404, detail="Pescador não encontrado")
    return {"message": "Pescador removido com sucesso"}
