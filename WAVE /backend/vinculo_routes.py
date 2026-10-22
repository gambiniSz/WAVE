"""Vínculos N:N do pescador com locais de pesca e equipamentos."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import Equipamento, LocalPesca, Pescador, pescador_equipamento, pescador_local
from schemas import EquipamentoResponse, LocalPescaResponse
from security import get_current_user

router = APIRouter(prefix="/api/pescadores", tags=["Vínculos do Pescador"])


def _so_o_proprio(id_pescador: int, usuario: Pescador):
    if id_pescador != usuario.id_pescador:
        raise HTTPException(status_code=403, detail="Você só pode alterar os seus próprios vínculos")


async def _listar(db, modelo, pk, tabela, col, id_pescador):
    consulta = (
        select(modelo)
        .join(tabela, tabela.c[col] == pk)
        .where(tabela.c.id_pescador == id_pescador)
        .order_by(pk)
    )
    return (await db.execute(consulta)).scalars().all()


async def _vincular(db, modelo, tabela, col, id_item, id_pescador, nome):
    if not await db.get(modelo, id_item):
        raise HTTPException(status_code=404, detail=f"{nome} não encontrado")
    ja_existe = await db.execute(
        select(tabela).where(tabela.c.id_pescador == id_pescador, tabela.c[col] == id_item)
    )
    if ja_existe.first():
        raise HTTPException(status_code=409, detail="Vínculo já existe")
    await db.execute(insert(tabela).values(id_pescador=id_pescador, **{col: id_item}))
    await db.commit()
    return {"message": "Vínculo criado com sucesso"}


async def _desvincular(db, tabela, col, id_item, id_pescador):
    resultado = await db.execute(
        delete(tabela).where(tabela.c.id_pescador == id_pescador, tabela.c[col] == id_item)
    )
    if resultado.rowcount == 0:
        raise HTTPException(status_code=404, detail="Vínculo não encontrado")
    await db.commit()
    return {"message": "Vínculo removido com sucesso"}


# ---------- Locais ----------
@router.get("/{id_pescador}/locais", response_model=List[LocalPescaResponse])
async def listar_locais(
    id_pescador: int, _: Pescador = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    if not await db.get(Pescador, id_pescador):
        raise HTTPException(status_code=404, detail="Pescador não encontrado")
    return await _listar(db, LocalPesca, LocalPesca.id_local, pescador_local, "id_local", id_pescador)


@router.post("/{id_pescador}/locais/{id_local}", status_code=status.HTTP_201_CREATED)
async def vincular_local(
    id_pescador: int, id_local: int,
    usuario: Pescador = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    _so_o_proprio(id_pescador, usuario)
    return await _vincular(db, LocalPesca, pescador_local, "id_local", id_local, id_pescador, "Local")


@router.delete("/{id_pescador}/locais/{id_local}")
async def desvincular_local(
    id_pescador: int, id_local: int,
    usuario: Pescador = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    _so_o_proprio(id_pescador, usuario)
    return await _desvincular(db, pescador_local, "id_local", id_local, id_pescador)


# ---------- Equipamentos ----------
@router.get("/{id_pescador}/equipamentos", response_model=List[EquipamentoResponse])
async def listar_equipamentos(
    id_pescador: int, _: Pescador = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    if not await db.get(Pescador, id_pescador):
        raise HTTPException(status_code=404, detail="Pescador não encontrado")
    return await _listar(
        db, Equipamento, Equipamento.id_equipamento, pescador_equipamento, "id_equipamento", id_pescador
    )


@router.post("/{id_pescador}/equipamentos/{id_equipamento}", status_code=status.HTTP_201_CREATED)
async def vincular_equipamento(
    id_pescador: int, id_equipamento: int,
    usuario: Pescador = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    _so_o_proprio(id_pescador, usuario)
    return await _vincular(
        db, Equipamento, pescador_equipamento, "id_equipamento", id_equipamento, id_pescador, "Equipamento"
    )


@router.delete("/{id_pescador}/equipamentos/{id_equipamento}")
async def desvincular_equipamento(
    id_pescador: int, id_equipamento: int,
    usuario: Pescador = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    _so_o_proprio(id_pescador, usuario)
    return await _desvincular(db, pescador_equipamento, "id_equipamento", id_equipamento, id_pescador)
