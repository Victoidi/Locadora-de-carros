# Pasta `templates`

Templates HTML renderizados no servidor Flask usando Jinja2.

## Arquivos

- `base.html`: layout base compartilhado entre paginas (estrutura comum, navegacao e blocos Jinja).
- `login.html`: tela de autenticacao de funcionario.
- `register.html`: tela de cadastro de funcionario.
- `dashboard.html`: painel principal com indicadores operacionais.
- `clientes.html`: tela de cadastro e listagem de clientes.
- `inventario.html`: tela de cadastro e consulta de veiculos com filtros.
- `pagamentos.html`: tela de listagem de pagamentos.

## Convencoes

- Todos os templates de pagina devem estender `base.html` quando possivel.
- Mensagens de feedback usam `flash` no backend e devem ser exibidas de forma consistente no frontend.
- Campos de formularios devem manter nomes alinhados aos esperados nas rotas Flask.
