from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Enum
from infrastructure.database import Base

class Pedido(Base):
    __tablename__='pedido'

    id_pedido= Column(Integer,primary_key= True, index= True)
    id_cliente= Column(Integer, ForeignKey('cliente.id_cliente'), nullable= False)
    id_unidade= Column(Integer, ForeignKey('unidade.id_unidade'), nullable= False)
    data_pedido= Column(DateTime, default=datetime.now)
    canal_pedido= Column(Enum('APP', 'TOTEM', 'BALCAO', 'PICKUP', 'WEB'), nullable= False)
    status_pedido= Column(String(20), default= 'RECEBIDO', nullable= False)
    valor_total= Column(Numeric(10,2), nullable= False)