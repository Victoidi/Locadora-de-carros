# Pasta `src`

Contem o codigo-fonte principal da aplicacao Flask.

## Arquivos

- `app.py`: ponto de entrada da aplicacao.
  - Define `app` Flask.
  - Implementa autenticacao de sessao.
  - Registra rotas de login, cadastro, dashboard, clientes, inventario e pagamentos.
  - Faz consultas e insercoes no MySQL com tratamento de erros.
  - Expone `GET /health` para monitoramento.
- `database.py`: fabrica de conexao com MySQL.
  - Le configuracoes via variaveis de ambiente (`DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`).
  - Retorna conexao `mysql-connector-python`.
- `__init__.py`: marca o diretorio como pacote Python.

## Decisoes tecnicas

- Uso de `mysql-connector-python` para conexao direta com banco.
- Uso de `werkzeug.security` para hash e validacao de senha.
- Uso de `flask.session` para controle de autenticacao.
- Separacao da conexao ao banco em modulo proprio para facilitar manutencao.
