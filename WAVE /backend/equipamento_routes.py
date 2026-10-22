from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db
from models import Equipamento
from schemas import EquipamentoCreate, EquipamentoResponse

router = APIRouter(prefix="/api/equipamentos", tags=["Equipamentos"])


@router.post("/", response_model=EquipamentoResponse, status_code=status.HTTP_201_CREATED)
async def criar(equipamento: EquipamentoCreate, db: AsyncSession = Depends(get_db)):
    db_equip = Equipamento(**equipamento.model_dump())
    db.add(db_equip)
    await db.commit()
    await db.refresh(db_equip)
    return db_equip


@router.get("/", response_model=List[EquipamentoResponse])
async def listar(db: AsyncSession = Depends(get_db)):
    resultado = await db.execute(select(Equipamento).order_by(Equipamento.id_equipamento))
    return resultado.scalars().all()


@router.put("/{id_equipamento}", response_model=EquipamentoResponse)
async def atualizar(id_equipamento: int, dados: EquipamentoCreate, db: AsyncSession = Depends(get_db)):
    equip = await db.get(Equipamento, id_equipamento)
    if not equip:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado")
    for chave, valor in dados.model_dump().items():
        setattr(equip, chave, valor)
    await db.commit()
    await db.refresh(equip)
    return equip


@router.delete("/{id_equipamento}")
async def deletar(id_equipamento: int, db: AsyncSession = Depends(get_db)):
    resultado = await db.execute(
        select(Equipamento)
        .options(selectinload(Equipamento.pescadores))
        .where(Equipamento.id_equipamento == id_equipamento)
    )
    equip = resultado.scalar_one_or_none()
    if not equip:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado")
    await db.delete(equip)
    await db.commit()
    return {"message": "Equipamento removido com sucesso"}
