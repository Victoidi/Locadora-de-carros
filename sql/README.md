# Pasta `sql`

Scripts SQL usados para preparar o banco de dados da aplicacao.

## Arquivos

- `create_funcionario_table.sql`:
  - Seleciona o banco `LOCADORA_CARROS`.
  - Cria a tabela `funcionario` caso ela nao exista.
  - Define constraints de unicidade para login, email e CPF.
  - Inclui colunas de auditoria basicas (`dt_criacao`) e status (`st_ativo`).

## Como usar

1. Crie o schema `LOCADORA_CARROS` no MySQL.
2. Execute os scripts desta pasta na ordem desejada.
3. Verifique se o usuario definido em `DB_USER` possui permissoes de leitura e escrita.

## Boas praticas

- Versionar novos scripts de forma incremental.
- Evitar edicoes destrutivas diretas em scripts ja aplicados em producao.
