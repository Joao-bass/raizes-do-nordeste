from sqlalchemy import Column, Integer, String, Text, Boolean, Numeric
from infrastructure.database import Base

class Produto(Base):
    __tablename__= 'produto'

    id_produto= Column(Integer, primary_key= True, index= True)
    nome= Column(String(100), nullable= False)
    descricao= Column(Text)
    ingredientes= Column(Text)
    preco= Column(Numeric(10,2), nullable= False)
    categoria= Column(String(20), nullable= False)
    ativo= Column(Boolean, default= True, nullable= False)
