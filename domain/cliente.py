from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from infrastructure.database import Base

class Cliente(Base):
    __tablename__= 'cliente'

    id_cliente= Column(Integer, primary_key= True, index= True)
    nome= Column(String(100), nullable= False)
    email= Column(String(100), unique= True, nullable= False)
    senha_hash= Column(String(255), nullable= False)
    endereco= Column(Text)
    data_cadastro= Column(DateTime, default= datetime.now)
    perfil= Column(String(20), default= 'CLIENTE', nullable= False)
