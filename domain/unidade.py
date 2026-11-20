from sqlalchemy import Column, Integer, String, Boolean
from infrastructure.database import Base

class Unidade(Base):
    __tablename__= 'unidade'

    id_unidade= Column(Integer, primary_key= True, index= True)
    nome= Column(String(100), nullable= False)
    endereco= Column(String(200), nullable= False)
    cidade= Column(String(100), nullable= False)
    estado= Column(String(2), nullable= False)
    ativo= Column(Boolean, default= True, nullable= False)
    