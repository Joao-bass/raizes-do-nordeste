from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from infrastructure.database import Base

class PontosFidelidade(Base):
    __tablename__ = 'pontos_fidelidade'

    id_pontos = Column(Integer, primary_key=True, index=True)
    id_cliente = Column(Integer, ForeignKey('cliente.id_cliente'), nullable=False)
    pontos = Column(Integer, nullable=False)
    data_movimentacao = Column(DateTime, default=datetime.now)
    tipo = Column(String(20), nullable=False)
    observacao = Column(Text)