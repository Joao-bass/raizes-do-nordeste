from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from infrastructure.database import Base

class Estoque(Base):
    __tablename__= 'estoque'

    id_estoque= Column(Integer, primary_key= True, index= True)
    id_produto= Column(Integer, ForeignKey('produto.id_produto'), nullable= False)
    id_unidade= Column(Integer, ForeignKey('unidade.id_unidade'), nullable= False)
    quantidade_atual= Column(Integer, nullable= False)
    quantidade_minima= Column(Integer, nullable= False)
    data_atualizacao= Column(DateTime, default=datetime.now)
