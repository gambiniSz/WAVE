from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

import chatbot_service
from database import get_db
from models import Chatbot, Clima, LocalPesca, Pescador, pescador_local
from pagination import Paginacao
from schemas import ChatbotPergunta, ChatbotResponse
from security import get_current_user

router = APIRouter(prefix="/api/chatbot", tags=["Chatbot"])


async def _contexto(db: AsyncSession, pescador: Pescador) -> str:
    locais = (
        await db.execute(
            select(LocalPesca)
            .join(pescador_local, pescador_local.c.id_local == LocalPesca.id_local)
            .where(pescador_local.c.id_pescador == pescador.id_pescador)
            .order_by(LocalPesca.id_local)
            .limit(10)
        )
    ).scalars().all()

    linhas = [f"Pescador: {pescador.nome}"]
    if not locais:
        linhas.append("Nenhum local de pesca vinculado.")
    for local in locais:
        clima = (
            await db.execute(
                select(Clima)
                .where(Clima.id_local == local.id_local)
                .order_by(Clima.data_registro.desc(), Clima.id_clima.desc())
                .limit(1)
            )
        ).scalar_one_or_none()
        linha = f"- {local.nome_area}"
        if local.situacao:
            linha += f" (situação: {local.situacao})"
        if clima:
            linha += f": {clima.condicao or 'sem condição'}"
            if clima.temperatura is not None:
                linha += f", {clima.temperatura}°C"
            linha += f" em {clima.data_registro.isoformat()}"
        else:
            linha += ": sem registro de clima"
        linhas.append(linha)
    return "\n".join(linhas)


@router.post("/", response_model=ChatbotResponse, status_code=status.HTTP_201_CREATED)
async def perguntar(
    dados: ChatbotPergunta,
    usuario: Pescador = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    contexto = await _contexto(db, usuario)
    resposta = await chatbot_service.gerar_resposta(dados.pergunta, contexto)
    registro = Chatbot(
        id_pescador=usuario.id_pescador,
        pergunta=dados.pergunta,
        resposta=resposta,
        data_pergunta=date.today(),
    )
    db.add(registro)
    await db.commit()
    await db.refresh(registro)
    return registro


@router.get("/", response_model=List[ChatbotResponse])
async def historico(
    p: Paginacao = Depends(),
    usuario: Pescador = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    resultado = await db.execute(
        select(Chatbot)
        .where(Chatbot.id_pescador == usuario.id_pescador)
        .order_by(Chatbot.id_chatbot.desc())
        .offset(p.skip)
        .limit(p.limit)
    )
    return resultado.scalars().all()


@router.delete("/{id_chatbot}")
async def deletar(
    id_chatbot: int,
    usuario: Pescador = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    registro = await db.get(Chatbot, id_chatbot)
    if not registro or registro.id_pescador != usuario.id_pescador:
        raise HTTPException(status_code=404, detail="Mensagem não encontrada")
    await db.delete(registro)
    await db.commit()
    return {"message": "Mensagem removida com sucesso"}


@router.delete("/")
async def limpar_historico(
    usuario: Pescador = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    await db.execute(delete(Chatbot).where(Chatbot.id_pescador == usuario.id_pescador))
    await db.commit()
    return {"message": "Histórico removido com sucesso"}
