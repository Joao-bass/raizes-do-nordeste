from sqlalchemy import Column, Integer, String, Date, Text
from infrastructure.database import Base


class Campanha(Base):
    __tablename__= 'campanha'

    id_campanha= Column(Integer, primary_key= True, index= True)
    nome= Column(String(100), nullable= False)
    descricao= Column(Text)
    tipo= Column(String(50), nullable= False)
    data_inicio= Column(Date, nullable= False)
    data_fim= Column(Date, nullable= False)
    idade_minima= Column(Integer)
    idade_maxima= Column(Integer)
    frequencia_maxima= Column(Integer)
    perfil_alvo= Column(String(100))
    ativo= Column(Integer, default= 1, nullable= False)
