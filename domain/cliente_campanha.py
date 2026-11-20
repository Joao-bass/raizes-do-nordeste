from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Boolean, ForeignKey
from infrastructure.database import Base

class ClienteCampanha(Base):
    __tablename__= 'cliente_campanha'

    id_cliente_campanha= Column(Integer, primary_key= True, index= True)
    id_cliente= Column(Integer, ForeignKey('cliente.id_cliente'), nullable= False)
    id_campanha= Column(Integer, ForeignKey('campanha.id_campanha'), nullable= False)
    data_inscricao= Column(DateTime, default=datetime.now)
    consentimento= Column(Boolean, default= False, nullable= False)
    data_consentimento= Column(DateTime)

    