from sqlalchemy import Column, Integer, ForeignKey, Numeric
from infrastructure.database import Base

class ItemPedido(Base):
    __tablename__= 'item_pedido'

    id_item_pedido= Column(Integer, primary_key= True, index= True)
    id_pedido= Column(Integer, ForeignKey('pedido.id_pedido'), nullable= False)
    id_produto= Column(Integer, ForeignKey('produto.id_produto'), nullable= False)
    quantidade= Column(Integer, nullable= False)
    preco_unitario= Column(Numeric(10,2), nullable= False)
    subtotal= Column(Numeric(10,2), nullable= False)
    
                     