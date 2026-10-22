from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import Pescador
from schemas import PescadorCreate


async def criar_pescador(db: AsyncSession, dados: PescadorCreate):
    db_pescador = Pescador(**dados.model_dump())
    db.add(db_pescador)
    await db.commit()
    await db.refresh(db_pescador)
    return db_pescador


async def listar_pescadores(db: AsyncSession):
    resultado = await db.execute(select(Pescador).order_by(Pescador.id_pescador))
    return resultado.scalars().all()


async def buscar_pescador_por_id(db: AsyncSession, id_pescador: int):
    return await db.get(Pescador, id_pescador)


async def atualizar_pescador(db: AsyncSession, id_pescador: int, dados: PescadorCreate):
    db_pescador = await db.get(Pescador, id_pescador)
    if not db_pescador:
        return None
    for chave, valor in dados.model_dump().items():
        setattr(db_pescador, chave, valor)
    await db.commit()
    await db.refresh(db_pescador)
    return db_pescador


async def deletar_pescador(db: AsyncSession, id_pescador: int):
    # Carrega as relações antes de apagar: no modo assíncrono o cascade
    # do SQLAlchemy não consegue carregá-las sozinho.
    resultado = await db.execute(
        select(Pescador)
        .options(
            selectinload(Pescador.chatbots),
            selectinload(Pescador.vendas),
            selectinload(Pescador.locais),
            selectinload(Pescador.equipamentos),
        )
        .where(Pescador.id_pescador == id_pescador)
    )
    db_pescador = resultado.scalar_one_or_none()
    if not db_pescador:
        return False
    await db.delete(db_pescador)
    await db.commit()
    return True
