from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from infrastructure.database import Base

class MovimentacaoEstoque(Base):
    __tablename__= 'movimentacao_estoque'

    id_movimentacao= Column(Integer, primary_key= True, index= True)
    id_estoque= Column(Integer, ForeignKey('estoque.id_estoque'), nullable= False)
    tipo= Column(String(10), nullable= False)
    quantidade= Column(Integer, nullable= False)
    motivo= Column(String(100), nullable= False)
    data_movimentacao= Column(DateTime, default=datetime.now)
    usuario= Column(String(100), nullable= False)
