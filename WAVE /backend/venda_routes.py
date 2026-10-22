from datetime import date
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import Pescador, Venda
from pagination import Paginacao
from schemas import VendaCreate, VendaResponse, VendaResumo
from security import get_current_user

router = APIRouter(prefix="/api/vendas", tags=["Vendas"])


def _filtrar(consulta, id_pescador: int, data_inicio: Optional[date], data_fim: Optional[date]):
    consulta = consulta.where(Venda.id_pescador == id_pescador)
    if data_inicio:
        consulta = consulta.where(Venda.data_venda >= data_inicio)
    if data_fim:
        consulta = consulta.where(Venda.data_venda <= data_fim)
    return consulta


async def _venda_do_usuario(db: AsyncSession, id_venda: int, usuario: Pescador) -> Venda:
    venda = await db.get(Venda, id_venda)
    # 404 também quando é de outro pescador, para não revelar que existe
    if not venda or venda.id_pescador != usuario.id_pescador:
        raise HTTPException(status_code=404, detail="Venda não encontrada")
    return venda


@router.post("/", response_model=VendaResponse, status_code=status.HTTP_201_CREATED)
async def criar(
    venda: VendaCreate,
    usuario: Pescador = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    db_venda = Venda(**venda.model_dump(), id_pescador=usuario.id_pescador)
    db.add(db_venda)
    await db.commit()
    await db.refresh(db_venda)
    return db_venda


@router.get("/", response_model=List[VendaResponse])
async def listar(
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    p: Paginacao = Depends(),
    usuario: Pescador = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    consulta = _filtrar(select(Venda), usuario.id_pescador, data_inicio, data_fim)
    consulta = consulta.order_by(Venda.data_venda, Venda.id_venda).offset(p.skip).limit(p.limit)
    resultado = await db.execute(consulta)
    return resultado.scalars().all()


@router.get("/resumo", response_model=VendaResumo)
async def resumo(
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    usuario: Pescador = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    consulta = _filtrar(
        select(func.coalesce(func.sum(Venda.valor), 0), func.count(Venda.id_venda)),
        usuario.id_pescador, data_inicio, data_fim,
    )
    total, quantidade = (await db.execute(consulta)).one()
    return VendaResumo(total=Decimal(total), quantidade=quantidade)


@router.get("/{id_venda}", response_model=VendaResponse)
async def buscar(
    id_venda: int,
    usuario: Pescador = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _venda_do_usuario(db, id_venda, usuario)


@router.put("/{id_venda}", response_model=VendaResponse)
async def atualizar(
    id_venda: int,
    dados: VendaCreate,
    usuario: Pescador = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    venda = await _venda_do_usuario(db, id_venda, usuario)
    for chave, valor in dados.model_dump().items():
        setattr(venda, chave, valor)
    await db.commit()
    await db.refresh(venda)
    return venda


@router.delete("/{id_venda}")
async def deletar(
    id_venda: int,
    usuario: Pescador = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    venda = await _venda_do_usuario(db, id_venda, usuario)
    await db.delete(venda)
    await db.commit()
    return {"message": "Venda removida com sucesso"}
