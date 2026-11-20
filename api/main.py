from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import FastAPI, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from pwdlib import PasswordHash
from infrastructure.database import Base, engine, sessionLocal
from sqlalchemy import select
from jose import jwt
from datetime import datetime, timedelta, timezone, date
from enum import Enum


class CanalPedido(str,Enum):
    APP= 'APP'
    TOTEM= 'TOTEM'
    BALCAO= 'BALCAO'
    PICKUP= 'PICKUP'
    WEB= 'WEB'

class MetodoPagamento(str, Enum):
    CREDITO= 'CREDITO'
    DEBITO= 'DEBITO'
    PIX= 'PIX' 

password_hash= PasswordHash.recommended()

SECRET_KEY= 'chave-secreta-raizes'
ALGORITHM= 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES= 30

def criar_token(dados: dict):
    dados_token= dados.copy()
    expiracao= datetime.now(timezone.utc)+ timedelta(minutes= ACCESS_TOKEN_EXPIRE_MINUTES)
    dados_token.update({'exp': expiracao})

    token= jwt.encode(dados_token, SECRET_KEY, algorithm= ALGORITHM)
    return token

seguranca= HTTPBearer(auto_error= False)

def verificar_perfil(perfil: str):
    def validar_token(credenciais: HTTPAuthorizationCredentials= Depends(seguranca)):
        if credenciais is None:
            raise HTTPException(status_code= 401, detail= 'Token nao informado')

        try:
            dados= jwt.decode(
                credenciais.credentials,
                SECRET_KEY,
                algorithms= [ALGORITHM]
            )
        except Exception:
            raise HTTPException(status_code= 401, detail= 'Token invalido')

        if dados.get('perfil')!= perfil:
            raise HTTPException(status_code= 403, detail= 'Acesso nao permitido')

        return dados
    
    return validar_token



from domain.cliente import Cliente
from domain.produto import Produto
from domain.unidade import Unidade
from domain.estoque import Estoque
from domain.movi_estoque import MovimentacaoEstoque
from domain.pedido import Pedido
from domain.item_pedido import ItemPedido
from domain.pagamento import Pagamento
from domain.fidelidade import PontosFidelidade
from domain.cliente_campanha import ClienteCampanha
from domain.campanha import Campanha
from domain.relatorio_vendas import RelatorioVendas
from domain.log_auditoria import LogAuditoria



app= FastAPI()



@app.exception_handler(HTTPException)
async def tratar_erro(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code= exc.status_code, 
        content={
            'error': 'ERRO',
            'message': exc.detail,
            'details': [],
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'path': request.url.path
        }
    )

@app.exception_handler(RequestValidationError)
async def tratar_erro_validacao(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code= 422,
        content={
            'error': 'ERRO DE VALIDACAO',
            'message': 'Dados invalidos',
            'details': jsonable_encoder(exc.errors()),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'path': request.url.path
        }
    )

@app.exception_handler(Exception)
async def tratar_erro_interno(request: Request, exc: Exception):
    return JSONResponse(
        status_code= 500,
        content={
            'error': 'ERRO INTERNO',
            'message': 'Ocorreu um erro interno',
            'details': [],
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'path': request.url.path
        }
    )



class CriarCliente(BaseModel):
    nome: str
    email: str
    senha: str
    endereco: str
    
class Login(BaseModel):
    email: str
    senha: str

class CriarPedido(BaseModel):
    id_cliente: int
    id_unidade: int
    canal_pedido: CanalPedido

class AdicionarItemPedido(BaseModel):
    id_pedido: int
    id_produto: int
    quantidade: int= Field(gt= 0)

class AtualizarStatus(BaseModel):
    status_pedido: str

class CriarPagamento(BaseModel):
    id_pedido: int
    metodo: MetodoPagamento

class AtualizarPagamento(BaseModel):
    status: str
    resposta_gateway: str

class Resgatepontos(BaseModel):
    id_cliente: int
    id_pedido: int

class MovimentaEstoque(BaseModel):
    id_estoque: int
    tipo: str
    quantidade: int
    motivo: str
    usuario: str

class CriarCampanha(BaseModel):
    nome: str
    descricao: str
    tipo: str
    data_inicio: date
    data_fim: date
    idade_minima: int
    idade_maxima: int
    frequencia_maxima: int
    perfil_alvo: str

class InscricaoCampanha(BaseModel):
    id_cliente: int
    id_campanha: int
    consentimento: bool

class CriarRelatorio(BaseModel):
    id_unidade: int
    periodo: str

class CriarLog(BaseModel):
    usuario: str
    acao: str
    entidade: str
    entidade_id: int
    detalhes: str







def get_db():
    db= sessionLocal()
    try:
        yield db
    finally:
        db.close()




@app.post('/clientes')
def criar_cliente(cliente: CriarCliente, db= Depends(get_db)):
        cliente_existe= db.query(Cliente).filter(
            Cliente.email== cliente.email).first()
        if cliente_existe:
             raise HTTPException(status_code= 400, detail='Email ja cadastrado')   
        
        
        novo_cliente= Cliente(
            nome= cliente.nome,
            email= cliente.email,
            senha_hash= password_hash.hash(cliente.senha),
            endereco= cliente.endereco
            )


        db.add(novo_cliente)
        db.commit()
        db.refresh(novo_cliente)


        return{
             'id_cliente': novo_cliente.id_cliente,
             'nome': novo_cliente.nome,
             'email': novo_cliente.email,
             'endereco': novo_cliente.endereco,
             'data_cadastro': novo_cliente.data_cadastro
        }


@app.post('/login')
def login(dados: Login, db= Depends(get_db)):
    cliente= db.query(Cliente).filter(
          Cliente.email== dados.email).first()
    if not cliente:
        raise HTTPException(status_code= 404, detail= 'Cliente nao encontrado')
    if not password_hash.verify(dados.senha, cliente.senha_hash):
         raise HTTPException(status_code= 401, detail= 'senha invalida/')

    token= criar_token({'sub': str(cliente.id_cliente),
                        'perfil': cliente.perfil})

    return{
        'mensagem': 'login realizado com sucesso.',
        'id_cliente': cliente.id_cliente,
        'nome': cliente.nome,
        'email': cliente.email,
        'access_token': token,
        'token_type': 'bearer'
    }


@app.get('/produtos')
def listar_produtos(id_unidade: int, db= Depends(get_db)):
    produtos= db.query(Produto).join(
        Estoque, Produto.id_produto== Estoque.id_produto).filter(
            Estoque.id_unidade== id_unidade,
            Estoque.quantidade_atual> 0,
            Produto.ativo== True).all()
    return produtos
    

@app.get('/unidades')
def lista_unidade(db= Depends(get_db)):
    unidade= db.query(Unidade).filter(
        Unidade.ativo== True).all()
    return unidade 


@app.post('/pedidos')
def criar_pedido(dados: CriarPedido, db= Depends(get_db),
                 usuario= Depends(verificar_perfil('CLIENTE'))):
    if dados.id_cliente!= int(usuario['sub']):
        raise HTTPException(status_code= 403, detail= 'Acesso nao permitido')

    unidade= db.query(Unidade).filter(
        Unidade.id_unidade== dados.id_unidade).first()
    if not unidade:
        raise HTTPException(status_code= 404, detail= 'Unidade nao encontrada')


    novo_pedido= Pedido(
        id_cliente= int(usuario['sub']),
        id_unidade= dados.id_unidade,
        canal_pedido= dados.canal_pedido,
        status_pedido= 'Pedido recebido',
        valor_total= 0
    )

    db.add(novo_pedido)
    db.commit()
    db.refresh(novo_pedido)

    log= LogAuditoria(
            usuario= usuario['sub'],
            acao= 'Criacao pedido',
            entidade= 'Pedido',
            entidade_id= novo_pedido.id_pedido,
            detalhes= 'Pedido criado '
        )
    db.add(log)
    db.commit()

    return novo_pedido


@app.post('/pedidos/itens')
def adicionar_item(dados: AdicionarItemPedido, db= Depends(get_db),
                   usuario= Depends(verificar_perfil('CLIENTE'))):
    
    pedido= db.query(Pedido).filter(
        Pedido.id_pedido== dados.id_pedido).first()
    if not pedido:
        raise HTTPException(status_code= 404, detail= 'Pedido nao encontrado')
    if pedido.id_cliente!= int(usuario['sub']):
        raise HTTPException(status_code= 403, detail= 'Acesso nao permitido')
    
    
    produto= db.query(Produto).filter(
        Produto.id_produto== dados.id_produto).first()
    if not produto:
        raise HTTPException(status_code= 404, detail= 'Produto nao encontrado')
    
    estoque= db.query(Estoque).filter(
        Estoque.id_produto== dados.id_produto,
        Estoque.id_unidade== pedido.id_unidade).first()
    if not estoque or estoque.quantidade_atual < dados.quantidade:
        raise HTTPException(status_code= 400, detail= 'Sem estoque')
    
    preco= produto.preco
    subtotal= preco * dados.quantidade
    novo_item= ItemPedido(
        id_pedido= dados.id_pedido,
        id_produto= dados.id_produto,
        quantidade= dados.quantidade,
        preco_unitario= preco,
        subtotal= subtotal)
    
    db.add(novo_item)
    db.commit()
    db.refresh(novo_item)

    estoque.quantidade_atual-= dados.quantidade
    db.commit()

    pedido.valor_total+= subtotal
    db.commit()
    db.refresh(pedido)

    return {
        'mensagem': 'Produto adicionado',
        'id_pedido': pedido.id_pedido,
        'valor_total': pedido.valor_total}


@app.get('/pedidos')
def listar_pedidos(canalPedido: CanalPedido= None, db= Depends(get_db),
                   usuario= Depends(verificar_perfil('CLIENTE'))):
    consulta= db.query(Pedido).filter(
        Pedido.id_cliente== int(usuario['sub'])
    )

    if canalPedido:
        consulta= consulta.filter(
            Pedido.canal_pedido== canalPedido
        )

    return consulta.all()


@app.get('/pedidos/{id_pedido}')
def consultar_pedido(id_pedido: int, db= Depends(get_db),
                     usuario= Depends(verificar_perfil('CLIENTE'))):
    
    pedido= db.query(Pedido).filter(
        Pedido.id_pedido== id_pedido).first()
    if not pedido:
        raise  HTTPException(status_code= 404, detail= 'Pedido nao encontrado')
    if pedido.id_cliente!= int(usuario['sub']):
        raise HTTPException(status_code= 403, detail= 'Acesso nao permitido')
    
    return{
        'id_pedido': pedido.id_pedido,
        'status_pedido': pedido.status_pedido,
        'valor_total': pedido.valor_total}


@app.put('/pedidos/{id_pedido}/status')
def att_status(id_pedido: int, dados: AtualizarStatus, db= Depends(get_db),
               usuario= Depends(verificar_perfil('ATENDENTE'))):
    
    pedido= db.query(Pedido).filter(
        Pedido.id_pedido== id_pedido).first()
    if not pedido:
        raise HTTPException(status_code= 404, detail= 'Pedido nao encontrado')

    ja_finalizado= pedido.status_pedido== 'Pedido finalizado'

    status_anterior= pedido.status_pedido
    pedido.status_pedido= dados.status_pedido
    

    log= LogAuditoria(
        usuario= usuario['sub'],
        acao= 'Alteracao status pedido',
        entidade= 'Pedido',
        entidade_id= pedido.id_pedido,
        detalhes= f'status alterado de {status_anterior} para {dados.status_pedido}'
    )
    db.add(log)

    if pedido.status_pedido== 'Pedido finalizado' and not ja_finalizado:
        pontos= PontosFidelidade(
            id_cliente= pedido.id_cliente,
            pontos= 3,
            tipo= 'credito',
            observacao= 'Pontos por pedido finalizado'
        )
        db.add(pontos)
    db.commit()

    return{'mensagem': 'status atualizado'}


@app.put('/pedidos/{id_pedido}/cancelar')
def cancelar_pedido(id_pedido: int, db= Depends(get_db),
                    usuario= Depends(verificar_perfil('CLIENTE'))):
    
    pedido= db.query(Pedido).filter(
        Pedido.id_pedido== id_pedido).first()
    if not pedido:
        raise HTTPException(status_code= 404, detail= 'Pedido nao encontrado')
    if pedido.id_cliente!= int(usuario['sub']):
        raise HTTPException(status_code= 403, detail= 'Acesso nao permitido')

    status_anterior= pedido.status_pedido
    pedido.status_pedido= 'Pedido cancelado'

    log= LogAuditoria(
            usuario= usuario['sub'],
            acao= 'Cancelamento pedido',
            entidade= 'Pedido',
            entidade_id= pedido.id_pedido,
            detalhes= f'status alterado de {status_anterior} para cancelado'
        )
    db.add(log)
    db.commit()

    return{'mensagem': 'Pedido cancelado'}


@app.post('/pagamentos')
def pagamento(dados: CriarPagamento, db= Depends(get_db),
              usuario= Depends(verificar_perfil('CLIENTE'))):
    
    pedido= db.query(Pedido).filter(
        Pedido.id_pedido== dados.id_pedido).first()
    if not pedido:
        raise HTTPException(status_code= 404, detail= 'Pedido nao encontrado')
    if pedido.id_cliente!= int(usuario['sub']):
        raise HTTPException(status_code= 403, detail= 'Acesso nao permitido')

    pagamento= Pagamento(
        id_pedido= dados.id_pedido,
        valor= pedido.valor_total,
        metodo = dados.metodo,
        status= 'Pendente')

    db.add(pagamento)
    db.commit()
    db.refresh(pagamento)

    return{
        'mensagem': 'Pagamento registrado',
        'id_pagamento': pagamento.id_pagamento,
        'status': pagamento.status
    }


@app.put('/pagamento/{id_pagamento}')
def atualizar_pagamento(id_pagamento: int, dados: AtualizarPagamento, db= Depends(get_db),
                        usuario= Depends(verificar_perfil('GERENTE'))):
    
    pagamento= db.query(Pagamento).filter(
        Pagamento.id_pagamento== id_pagamento).first()
    if not pagamento:
        raise HTTPException(status_code= 404,  detail= 'Pagamento nao encontrado ')

    pagamento.status= dados.status
    pagamento.resposta_gateway= dados.resposta_gateway

    if pagamento.status== 'Aprovado':
        pedido= db.query(Pedido).filter(
            Pedido.id_pedido== pagamento.id_pedido).first()
        if pedido:
            pedido.status_pedido= 'Pedido em preparo'

    db.commit()
    db.refresh(pagamento)
    
    return{
        'mensagem': 'Pagamento atualizado',
        'id_pagamento': pagamento.id_pagamento,
        'status': pagamento.status
    }


@app.get('/pontos/{id_cliente}')
def consultar_pontos(id_cliente: int, db= Depends(get_db),
                     usuario= Depends(verificar_perfil('CLIENTE'))):
    if id_cliente!= int(usuario['sub']):
        raise HTTPException(status_code= 403, detail= 'Acesso nao permitido')
    
    pontos= db.query(PontosFidelidade).filter(
        PontosFidelidade.id_cliente== int(usuario['sub'])).all()

    total= sum(
        item.pontos 
        if item.tipo== 'credito' 
        else- item.pontos for item in pontos)

    return{
        'id_cliente': id_cliente,
        'total_pontos': total
    }


@app.post('/pontos/resgate')
def resgate_pontos(dados: Resgatepontos, db= Depends(get_db),
                   usuario= Depends(verificar_perfil('CLIENTE'))):
    pedido= db.query(Pedido).filter(
        Pedido.id_pedido== dados.id_pedido,
        Pedido.id_cliente== int(usuario['sub'])).first()
    if not pedido:
        raise HTTPException(status_code= 404, detail= 'Pedido nao encontrado')

    movimentacoes= db.query(PontosFidelidade).filter(
        PontosFidelidade.id_cliente== int(usuario['sub'])).all()

    saldo= 0
    for item in movimentacoes:
        if item.tipo== 'credito':
            saldo+= item.pontos
        else:
            saldo-= item.pontos

    if saldo>= 100:
        desconto= 0.15
        usados= 100
    elif saldo>= 50:
        desconto= 0.05
        usados= 50
    else:
        raise HTTPException(status_code= 400, detail= 'Pontos insuficientes')


    pedido.valor_total-= pedido.valor_total * desconto
    db.commit()

    debito= PontosFidelidade(
        id_cliente= int(usuario['sub']),
        pontos= usados,
        tipo= 'debito',
        observacao= 'Resgate de pontos'
    )

    db.add(debito)
    db.commit()

    return{
        'mensagem': 'Desconto aplicado',
        'valor_total': pedido.valor_total,
        'pontos_utilizados': usados
    }


@app.post('/estoque/movimentacao')
def movimentar_estoque(dados: MovimentaEstoque, db= Depends(get_db),
                       usuario= Depends(verificar_perfil('GERENTE'))):
    
    estoque= db.query(Estoque).filter(
        Estoque.id_estoque== dados.id_estoque).first()
    if not estoque:
        raise HTTPException(status_code= 404, detail= 'Estoque nao encontrado')
    if dados.tipo== 'entrada':
        estoque.quantidade_atual+= dados.quantidade
    elif dados.tipo== 'saida':
        if estoque.quantidade_atual< dados.quantidade:
            raise HTTPException(status_code= 400, detail= 'Estoque insuficiente')
        estoque.quantidade_atual-= dados.quantidade
    else:
        raise HTTPException(status_code= 400, detail= 'Tipo invalido')

    movimentacao= MovimentacaoEstoque(
        id_estoque= dados.id_estoque,
        tipo= dados.tipo,
        quantidade= dados.quantidade,
        motivo= dados.motivo,
        usuario= usuario['sub']
    )

    db.add(movimentacao)

    log= LogAuditoria(
        usuario= usuario['sub'],
        acao= 'Movimentacao estoque',
        entidade= 'Estoque',
        entidade_id= dados.id_estoque,
        detalhes= f'{dados.tipo} de {dados.quantidade} unidades. Motivo: {dados.motivo}'
    )
    db.add(log)
    db.commit()

    return {'mensagem': 'Movimentacao registrada'}


@app.post('/campanhas')
def criar_campanha(dados: CriarCampanha, db= Depends(get_db),
                   usuario= Depends(verificar_perfil('GERENTE'))):
    
    campanha= Campanha(
        nome= dados.nome,
        descricao= dados.descricao,
        tipo= dados.tipo,
        data_inicio= dados.data_inicio,
        data_fim= dados.data_fim,
        idade_minima= dados.idade_minima,
        idade_maxima= dados.idade_maxima,
        frequencia_maxima= dados.frequencia_maxima,
        perfil_alvo= dados.perfil_alvo
    )

    db.add(campanha)
    db.commit()
    db.refresh(campanha)

    return{
        'mensagem': 'Campanha cadastrada',
        'id_campanha': campanha.id_campanha,
        'nome': campanha.nome
    }


@app.post('/campanhas/inscricao')
def inscrever_campanha(dados: InscricaoCampanha, db= Depends(get_db),
                        usuario= Depends(verificar_perfil('CLIENTE'))):
    if dados.id_cliente!= int(usuario['sub']):
        raise HTTPException(status_code= 403, detail= 'Acesso nao permitido')

    cliente= db.query(Cliente).filter(
        Cliente.id_cliente== int(usuario['sub'])).first()
    if not cliente:
        raise HTTPException(status_code= 404, detail= 'cliente nao encontrado')

    campanha= db.query(Campanha).filter(
        Campanha.id_campanha== dados.id_campanha).first()
    if not campanha:
        raise HTTPException(status_code= 404, detail= 'Campanha nao encontrada')

    inscricao= ClienteCampanha(
        id_cliente= int(usuario['sub']),
        id_campanha= dados.id_campanha,
        consentimento= dados.consentimento,
        data_consentimento= datetime.now()
        if dados.consentimento 
        else None
    )

    db.add(inscricao)
    db.commit()
    db.refresh(inscricao)

    return {'mensagem': 'Inscricao registrada'}


@app.get('/campanhas')
def listar_campanhas(db= Depends(get_db),
                     usuario= Depends(verificar_perfil('CLIENTE'))):
    campanhas= db.query(Campanha).filter(
        Campanha.ativo== 1).all()

    return campanhas


@app.post('/relatorios/vendas')
def criar_relatorio(dados: CriarRelatorio, db= Depends(get_db),
                    usuario= Depends(verificar_perfil('GERENTE'))):
    
    pedidos= db.query(Pedido).filter(
        Pedido.id_unidade== dados.id_unidade,
        Pedido.status_pedido== 'Pedido finalizado').all()

    total= sum(pedido.valor_total for pedido in pedidos)

    relatorio= RelatorioVendas(
        id_unidade= dados.id_unidade,
        periodo= dados.periodo,
        valor_total= total
    )

    db.add(relatorio)
    db.commit()
    db.refresh(relatorio)

    return{
        'mensagem': 'Relatorio gerado',
        'id_relatorio': relatorio.id_relatorio,
        'valor_total': relatorio.valor_total
    }


@app.get('/relatorios/vendas/{id_unidade}')
def listar_relatorios(id_unidade: int, db= Depends(get_db),
                      usuario= Depends(verificar_perfil('GERENTE'))):
    relatorios= db.query(RelatorioVendas).filter(
        RelatorioVendas.id_unidade== id_unidade).all()

    return relatorios


@app.post('/auditoria')
def criar_log(dados: CriarLog, db= Depends(get_db),
              usuario= Depends(verificar_perfil('GERENTE'))):
    log= LogAuditoria(
        usuario= usuario['sub'],
        acao= dados.acao,
        entidade= dados.entidade,
        entidade_id= dados.entidade_id,
        detalhes= dados.detalhes
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return{
        'mensagem': 'Log registrado',
        'id_log': log.id_log
    }





































Base.metadata.create_all(bind= engine)


