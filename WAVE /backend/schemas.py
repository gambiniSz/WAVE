from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------- Auth ----------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str = Field(min_length=1, max_length=72)


# ---------- Pescador ----------
class PescadorBase(BaseModel):
    nome: str = Field(min_length=1, max_length=255)
    email: EmailStr
    telefone: Optional[str] = Field(default=None, max_length=20)
    endereco: Optional[str] = Field(default=None, max_length=255)


class PescadorCreate(PescadorBase):
    senha: str = Field(min_length=6, max_length=72)


class PescadorUpdate(PescadorBase):
    pass


class PescadorResponse(PescadorBase, ORM):
    id_pescador: int


# ---------- Local de pesca ----------
class LocalPescaBase(BaseModel):
    nome_area: str = Field(min_length=1, max_length=255)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    situacao: Optional[str] = Field(default=None, max_length=100)
    descricao: Optional[str] = None


class LocalPescaCreate(LocalPescaBase):
    pass


class LocalPescaResponse(LocalPescaBase, ORM):
    id_local: int


# ---------- Venda ----------
class VendaBase(BaseModel):
    data_venda: date
    valor: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    descricao: Optional[str] = None


class VendaCreate(VendaBase):
    """O pescador dono da venda vem do token, não do corpo."""


class VendaResponse(VendaBase, ORM):
    id_venda: int
    id_pescador: int


class VendaResumo(BaseModel):
    total: Decimal
    quantidade: int


# ---------- Equipamento ----------
class EquipamentoBase(BaseModel):
    nome: str = Field(min_length=1, max_length=255)
    tipo: Optional[str] = Field(default=None, max_length=100)
    descricao: Optional[str] = None


class EquipamentoCreate(EquipamentoBase):
    pass


class EquipamentoResponse(EquipamentoBase, ORM):
    id_equipamento: int


# ---------- Clima ----------
class ClimaBase(BaseModel):
    id_local: int
    data_registro: date
    temperatura: Optional[float] = None
    condicao: Optional[str] = Field(default=None, max_length=100)
    descricao: Optional[str] = None


class ClimaCreate(ClimaBase):
    pass


class ClimaResponse(ClimaBase, ORM):
    id_clima: int


# ---------- Chatbot ----------
class ChatbotPergunta(BaseModel):
    pergunta: str = Field(min_length=1, max_length=2000)


class ChatbotResponse(ORM):
    id_chatbot: int
    id_pescador: int
    pergunta: str
    resposta: str
    data_pergunta: Optional[date] = None
