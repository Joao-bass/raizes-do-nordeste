from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from infrastructure.database import Base

class LogAuditoria(Base):
    __tablename__= 'log_auditoria'

    id_log= Column(Integer, primary_key= True, index= True)
    usuario= Column(String(100), nullable= False)
    acao= Column(String(100), nullable= False)
    entidade= Column(String(50), nullable= False)
    entidade_id= Column(Integer, nullable= False)
    data_hora= Column(DateTime, default=datetime.now)
    detalhes= Column(Text)