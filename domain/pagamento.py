from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Numeric
from infrastructure.database import Base

class Pagamento(Base):
    __tablename__= 'pagamento'

    id_pagamento= Column(Integer, primary_key= True, index= True)
    id_pedido= Column(Integer, ForeignKey('pedido.id_pedido'), nullable= False)
    metodo= Column(String(50), nullable= False)
    status= Column(String(30), nullable= False)
    valor= Column(Numeric(10,2), nullable= False)
    data_pagamento= Column(DateTime, default=datetime.now)
    resposta_gateway= Column(Text)
