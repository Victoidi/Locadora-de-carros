# Locadora de Carros

Aplicacao web em Flask para operacao interna de uma locadora, com autenticacao de funcionarios, dashboard e modulos de clientes, inventario e pagamentos.

## Estrutura do projeto

- `src/`: codigo Python da aplicacao (rotas, regras de negocio e conexao com banco).
- `templates/`: telas HTML renderizadas pelo Flask.
- `static/`: arquivos estaticos (CSS e imagens).
- `sql/`: scripts SQL de apoio para estrutura inicial do banco.
- `requirements.txt`: dependencias Python.
- `Procfile`, `Dockerfile`, `runtime.txt`: configuracoes de deploy.
- `.env.example`: exemplo de variaveis de ambiente.

## Funcionalidades principais

- Login de funcionario com hash de senha.
- Cadastro de funcionario.
- Dashboard com indicadores de marcas, veiculos, clientes e pagamentos.
- Cadastro e consulta de clientes.
- Cadastro e consulta de veiculos no inventario.
- Consulta de pagamentos com joins entre cliente, inventario e marca.
- Endpoint de verificacao de saude: `GET /health`.

## Requisitos

- Python 3.12+
- MySQL 8+

## Configuracao local

1. Crie e ative um ambiente virtual.
2. Instale dependencias:

```bash
pip install -r requirements.txt
```

3. Configure variaveis de ambiente usando `.env.example` como base:

- `SECRET_KEY`
- `PORT`
- `DB_HOST`
- `DB_PORT`
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`

4. Crie o banco e execute os scripts em `sql/`.

## Execucao

Desenvolvimento:

```bash
python -m flask --app src.app run
```

Producao (Gunicorn):

```bash
gunicorn src.app:app --bind 0.0.0.0:8080
```

## Deploy

O projeto ja inclui estrutura para deploy em plataformas com build Python ou Docker:

- `Procfile` para plataformas PaaS.
- `Dockerfile` para conteinerizacao.

## Observacoes

- Nao comite segredos reais no repositorio.
- Ajuste `SECRET_KEY` e credenciais do banco antes de publicar em producao.
