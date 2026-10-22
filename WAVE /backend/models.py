from sqlalchemy import Column, Integer, String, Text, Float, Date, Numeric, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base

pescador_local = Table(
    'pescador_local',
    Base.metadata,
    Column('id_pescador', Integer, ForeignKey('pescador.id_pescador', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True),
    Column('id_local', Integer, ForeignKey('local_pesca.id_local', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
)

pescador_equipamento = Table(
    'pescador_equipamento',
    Base.metadata,
    Column('id_pescador', Integer, ForeignKey('pescador.id_pescador', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True),
    Column('id_equipamento', Integer, ForeignKey('equipamento.id_equipamento', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
)

class Pescador(Base):
    __tablename__ = 'pescador'

    id_pescador = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    # nullable para não quebrar linhas antigas; quem não tem senha não consegue logar
    senha_hash = Column(String(255), nullable=True)
    telefone = Column(String(20), nullable=True)
    endereco = Column(String(255), nullable=True)

    chatbots = relationship('Chatbot', back_populates='pescador', cascade='all, delete-orphan')
    vendas = relationship('Venda', back_populates='pescador', cascade='all, delete-orphan')
    locais = relationship('LocalPesca', secondary=pescador_local, back_populates='pescadores')
    equipamentos = relationship('Equipamento', secondary=pescador_equipamento, back_populates='pescadores')

class LocalPesca(Base):
    __tablename__ = 'local_pesca'

    id_local = Column(Integer, primary_key=True, index=True)
    nome_area = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    situacao = Column(String(100), nullable=True)
    descricao = Column(Text, nullable=True)

    climas = relationship('Clima', back_populates='local', cascade='all, delete-orphan')
    pescadores = relationship('Pescador', secondary=pescador_local, back_populates='locais')

class Equipamento(Base):
    __tablename__ = 'equipamento'

    id_equipamento = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    tipo = Column(String(100), nullable=True)
    descricao = Column(Text, nullable=True)

    pescadores = relationship('Pescador', secondary=pescador_equipamento, back_populates='equipamentos')

class Chatbot(Base):
    __tablename__ = 'chatbot'

    id_chatbot = Column(Integer, primary_key=True, index=True)
    id_pescador = Column(Integer, ForeignKey('pescador.id_pescador', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    pergunta = Column(Text, nullable=False)
    resposta = Column(Text, nullable=False)
    data_pergunta = Column(Date, nullable=True)

    pescador = relationship('Pescador', back_populates='chatbots')

class Venda(Base):
    __tablename__ = 'venda'

    id_venda = Column(Integer, primary_key=True, index=True)
    id_pescador = Column(Integer, ForeignKey('pescador.id_pescador', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    data_venda = Column(Date, nullable=False)
    valor = Column(Numeric(10, 2), nullable=False)
    descricao = Column(Text, nullable=True)

    pescador = relationship('Pescador', back_populates='vendas')

class Clima(Base):
    __tablename__ = 'clima'

    id_clima = Column(Integer, primary_key=True, index=True)
    id_local = Column(Integer, ForeignKey('local_pesca.id_local', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    data_registro = Column(Date, nullable=False)
    temperatura = Column(Float, nullable=True)
    condicao = Column(String(100), nullable=True)
    descricao = Column(Text, nullable=True)

    local = relationship('LocalPesca', back_populates='climas')
