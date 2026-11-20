from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from infrastructure.database import Base

class RelatorioVendas(Base):
    __tablename__= 'relatorio_vendas'

    id_relatorio= Column(Integer, primary_key= True, index= True)
    id_unidade= Column(Integer, ForeignKey('unidade.id_unidade'), nullable= False)
    periodo= Column(String(50), nullable= False)
    valor_total= Column(Numeric(10,2), nullable= False)
    data_geracao= Column(DateTime, default=datetime.now)

    