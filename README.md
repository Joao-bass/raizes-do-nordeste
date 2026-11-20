# Raizes do nordeste 

API Back-End desenvolvida como projeto acadêmico do curso de Analise e Desenvolvimento de Sistemas da UNINTER.

## Tecnologias utilizadas

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- SQLite
- JWT
- Swagger/OpenAPI
- Postman

## Estrutura do projeto

api/: arquivo principal da API (main.py).
application/: funcionalidades da aplicacao.
domain/: componentes relacionados ao dominio.
infrastructure/: componentes de infraestrutura.
raizes.db: banco de dados SQLite.
requiriments.txt: arquivo com as dependências do projeto.

## Executando o projeto

1 - Instale o python.
2 - Abra o terminal na pasta do projeto.
3 - Crie o ambieste virtual:
    (python -m venv .venv)
4 - Ative o ambiente virtual:
    (.\.venv\Scripts\Activate.ps1)
5 - Instale as dependências:
    (python -m pip install -r requirements.txt)
6 - Execute a API:
    python -m uvicorn api.main:app --reload
 
Observação: Na primeira execução, é necessário criar o ambiente virtual e intalar as dependências.

## Documentação da API

apos iniciar a API, 
acesse: `http://127.0.0.1:8000/docs`

## Testes 

A coleção Postman contém requisições para testar as funcionalidades da API, incluindo cadastro, autenticação, pedidos, pagamentos e auditoria.
Para realizar os testes, importe a coleção Raizes do Nordeste.postman_collection.json no postman.
