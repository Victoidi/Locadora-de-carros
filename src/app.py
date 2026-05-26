from decimal import Decimal, InvalidOperation
from functools import wraps
import os

from flask import Flask, flash, redirect, render_template, request, session, url_for
from mysql.connector import Error
from mysql.connector.errors import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from src.database import get_connection

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)
app.secret_key = os.getenv("SECRET_KEY", "troque-esta-chave-secreta")


def close_db_resources(cursor=None, connection=None):
    """Fecha cursor e conexao com seguranca."""
    if cursor is not None:
        cursor.close()
    if connection is not None and connection.is_connected():
        connection.close()


def login_required(view_func):
    """Garante que apenas usuarios autenticados acessem a rota."""

    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Faca login para acessar a aplicacao.", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)

    return wrapped_view


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/health")
def health():
    return {"status": "ok"}, 200


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        identificador = request.form.get("identificador", "").strip()
        senha = request.form.get("senha", "")

        if not identificador or not senha:
            flash("Preencha login/email e senha.", "danger")
            return render_template("login.html")

        connection = None
        cursor = None
        try:
            connection = get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT id_funcionario, nm_primeiro, nm_ultimo, ds_senha_hash
                FROM funcionario
                WHERE (ds_email = %s OR ds_login = %s) AND st_ativo = TRUE
                LIMIT 1
                """,
                (identificador.lower(), identificador),
            )
            funcionario = cursor.fetchone()
        except Error:
            flash("Erro de conexao com o banco de dados.", "danger")
            return render_template("login.html")
        finally:
            close_db_resources(cursor, connection)

        if funcionario and check_password_hash(funcionario["ds_senha_hash"], senha):
            session["user_id"] = funcionario["id_funcionario"]
            session["user_name"] = (
                f"{funcionario['nm_primeiro']} {funcionario['nm_ultimo']}"
            )
            flash("Login realizado com sucesso.", "success")
            return redirect(url_for("dashboard"))

        flash("Login/email ou senha invalidos.", "danger")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        nm_primeiro = request.form.get("nm_primeiro", "").strip()
        nm_ultimo = request.form.get("nm_ultimo", "").strip()
        ds_login = request.form.get("ds_login", "").strip()
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        confirmar_senha = request.form.get("confirmar_senha", "")
        nr_telefone = request.form.get("nr_telefone", "").strip()
        nr_cpf = request.form.get("nr_cpf", "").strip()
        ds_cargo = request.form.get("ds_cargo", "").strip()
        dt_admissao = request.form.get("dt_admissao", "").strip()

        if not nm_primeiro or not nm_ultimo or not ds_login or not email or not senha:
            flash("Todos os campos sao obrigatorios.", "danger")
            return render_template("register.html")
        if len(senha) < 6:
            flash("A senha deve ter pelo menos 6 caracteres.", "danger")
            return render_template("register.html")
        if senha != confirmar_senha:
            flash("A confirmacao de senha nao confere.", "danger")
            return render_template("register.html")

        senha_hash = generate_password_hash(senha)
        connection = None
        cursor = None
        try:
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO funcionario
                (
                    nm_primeiro,
                    nm_ultimo,
                    ds_login,
                    ds_email,
                    ds_senha_hash,
                    nr_telefone,
                    nr_cpf,
                    ds_cargo,
                    dt_admissao
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    nm_primeiro,
                    nm_ultimo,
                    ds_login,
                    email,
                    senha_hash,
                    nr_telefone if nr_telefone else None,
                    nr_cpf if nr_cpf else None,
                    ds_cargo if ds_cargo else None,
                    dt_admissao if dt_admissao else None,
                ),
            )
            connection.commit()
            flash("Funcionario cadastrado com sucesso. Faca login.", "success")
            return redirect(url_for("login"))
        except IntegrityError:
            flash("Login, email ou CPF ja cadastrado.", "danger")
        except Error:
            flash("Nao foi possivel cadastrar funcionario por erro no banco.", "danger")
        finally:
            close_db_resources(cursor, connection)

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Sessao encerrada.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    estatisticas = {
        "total_marcas": 0,
        "total_veiculos": 0,
        "total_clientes": 0,
        "total_pagamentos": 0,
    }
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM marca) AS total_marcas,
                (SELECT COUNT(*) FROM inventario) AS total_veiculos,
                (SELECT COUNT(*) FROM cliente) AS total_clientes,
                (SELECT COUNT(*) FROM pagamento) AS total_pagamentos
            """
        )
        resultado = cursor.fetchone()
        if resultado:
            estatisticas = resultado
    except Error:
        flash("Nao foi possivel carregar os indicadores do dashboard.", "warning")
    finally:
        close_db_resources(cursor, connection)

    return render_template("dashboard.html", estatisticas=estatisticas)


@app.route("/clientes", methods=["GET", "POST"])
@login_required
def clientes():
    if request.method == "POST":
        nm_primeiro = request.form.get("nm_primeiro", "").strip()
        nm_ultimo = request.form.get("nm_ultimo", "").strip()
        ds_endereco = request.form.get("ds_endereco", "").strip()

        if not nm_primeiro or not nm_ultimo or not ds_endereco:
            flash("Preencha todos os campos do cliente.", "danger")
        else:
            connection = None
            cursor = None
            try:
                connection = get_connection()
                cursor = connection.cursor()
                cursor.execute(
                    """
                    INSERT INTO cliente (nm_primeiro, nm_ultimo, ds_endereco)
                    VALUES (%s, %s, %s)
                    """,
                    (nm_primeiro, nm_ultimo, ds_endereco),
                )
                connection.commit()
                flash("Cliente cadastrado com sucesso.", "success")
                return redirect(url_for("clientes"))
            except Error:
                flash("Erro ao cadastrar cliente no banco de dados.", "danger")
            finally:
                close_db_resources(cursor, connection)

    lista_clientes = []
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT nm_primeiro, nm_ultimo, ds_endereco
            FROM cliente
            ORDER BY id_cliente DESC
            LIMIT 20
            """
        )
        lista_clientes = cursor.fetchall()
    except Error:
        flash("Nao foi possivel consultar clientes.", "warning")
    finally:
        close_db_resources(cursor, connection)

    return render_template("clientes.html", clientes=lista_clientes)


@app.route("/inventario", methods=["GET", "POST"])
@login_required
def inventario():
    connection = None
    cursor = None
    marcas = []
    anos_disponiveis = []
    filtro_marca = request.args.get("marca", "").strip()
    filtro_ano = request.args.get("ano", "").strip()

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id_marca, nm_marca FROM marca ORDER BY nm_marca")
        marcas = cursor.fetchall()
    except Error:
        flash("Nao foi possivel carregar as marcas.", "danger")
    finally:
        close_db_resources(cursor, connection)

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT DISTINCT nr_ano
            FROM inventario
            WHERE nr_ano IS NOT NULL AND nr_ano <> ''
            ORDER BY nr_ano DESC
            """
        )
        anos_disponiveis = [row["nr_ano"] for row in cursor.fetchall()]
    except Error:
        flash("Nao foi possivel carregar os filtros de ano.", "warning")
    finally:
        close_db_resources(cursor, connection)

    if request.method == "POST":
        nm_modelo = request.form.get("nm_modelo", "").strip()
        nr_ano = request.form.get("nr_ano", "").strip()
        tp_transmissao = request.form.get("tp_transmissao", "").strip()
        tp_motor = request.form.get("tp_motor", "").strip()
        tp_combustivel = request.form.get("tp_combustivel", "").strip()
        vl_fipe_raw = request.form.get("vl_fipe", "").strip()
        vl_diaria_raw = request.form.get("vl_diaria", "").strip()
        id_marca_raw = request.form.get("id_marca", "").strip()

        if (
            not nm_modelo
            or not tp_transmissao
            or not tp_motor
            or not tp_combustivel
            or not vl_fipe_raw
            or not vl_diaria_raw
            or not id_marca_raw
        ):
            flash("Preencha todos os campos obrigatorios do veiculo.", "danger")
            return render_template(
                "inventario.html",
                marcas=marcas,
                anos_disponiveis=anos_disponiveis,
                filtro_marca=filtro_marca,
                filtro_ano=filtro_ano,
                veiculos=[],
            )

        if nr_ano and (not nr_ano.isdigit() or len(nr_ano) != 4):
            flash("Ano invalido. Informe 4 digitos.", "danger")
            return render_template(
                "inventario.html",
                marcas=marcas,
                anos_disponiveis=anos_disponiveis,
                filtro_marca=filtro_marca,
                filtro_ano=filtro_ano,
                veiculos=[],
            )

        try:
            vl_fipe = Decimal(vl_fipe_raw)
            if vl_fipe <= 0:
                raise InvalidOperation
        except InvalidOperation:
            flash("Valor FIPE invalido. Use formato decimal com ponto.", "danger")
            return render_template(
                "inventario.html",
                marcas=marcas,
                anos_disponiveis=anos_disponiveis,
                filtro_marca=filtro_marca,
                filtro_ano=filtro_ano,
                veiculos=[],
            )

        try:
            vl_diaria = Decimal(vl_diaria_raw)
            if vl_diaria <= 0:
                raise InvalidOperation
        except InvalidOperation:
            flash("Valor da diaria invalido. Use formato decimal com ponto.", "danger")
            return render_template(
                "inventario.html",
                marcas=marcas,
                anos_disponiveis=anos_disponiveis,
                filtro_marca=filtro_marca,
                filtro_ano=filtro_ano,
                veiculos=[],
            )

        try:
            id_marca = int(id_marca_raw)
        except ValueError:
            flash("Marca invalida.", "danger")
            return render_template(
                "inventario.html",
                marcas=marcas,
                anos_disponiveis=anos_disponiveis,
                filtro_marca=filtro_marca,
                filtro_ano=filtro_ano,
                veiculos=[],
            )

        connection = None
        cursor = None
        try:
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO inventario
                (
                    nm_modelo,
                    nr_ano,
                    tp_transmissao,
                    tp_motor,
                    tp_combustivel,
                    vl_fipe,
                    vl_diaria,
                    id_marca
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    nm_modelo,
                    nr_ano if nr_ano else None,
                    tp_transmissao,
                    tp_motor,
                    tp_combustivel,
                    vl_fipe,
                    vl_diaria,
                    id_marca,
                ),
            )
            connection.commit()
            flash("Veiculo cadastrado com sucesso.", "success")
            return redirect(url_for("inventario"))
        except Error:
            flash("Erro ao cadastrar veiculo no banco de dados.", "danger")
        finally:
            close_db_resources(cursor, connection)

    veiculos = []
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        filtros_where = []
        parametros = []

        if filtro_marca:
            filtros_where.append("m.nm_marca = %s")
            parametros.append(filtro_marca)
        if filtro_ano:
            filtros_where.append("i.nr_ano = %s")
            parametros.append(filtro_ano)

        sql_veiculos = """
            SELECT
                i.nm_modelo,
                i.nr_ano,
                i.tp_transmissao,
                i.tp_motor,
                i.tp_combustivel,
                i.vl_fipe,
                i.vl_diaria,
                m.nm_marca
            FROM inventario i
            JOIN marca m ON m.id_marca = i.id_marca
        """
        if filtros_where:
            sql_veiculos += " WHERE " + " AND ".join(filtros_where)
        sql_veiculos += " ORDER BY i.id_inventario DESC LIMIT 20"

        cursor.execute(sql_veiculos, tuple(parametros))
        veiculos = cursor.fetchall()
    except Error:
        flash("Nao foi possivel consultar inventario.", "warning")
    finally:
        close_db_resources(cursor, connection)

    return render_template(
        "inventario.html",
        marcas=marcas,
        anos_disponiveis=anos_disponiveis,
        filtro_marca=filtro_marca,
        filtro_ano=filtro_ano,
        veiculos=veiculos,
    )


@app.route("/pagamentos")
@login_required
def pagamentos():
    lista_pagamentos = []
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                CONCAT(c.nm_primeiro, ' ', c.nm_ultimo) AS nome_cliente,
                i.nm_modelo AS modelo_veiculo,
                m.nm_marca AS marca_veiculo,
                p.tp_pagamento,
                p.dt_data,
                p.qt_quantidade,
                i.vl_fipe,
                i.vl_diaria
            FROM pagamento p
            JOIN cliente c ON c.id_cliente = p.id_cliente
            JOIN inventario i ON i.id_inventario = p.id_inventario
            JOIN marca m ON m.id_marca = i.id_marca
            ORDER BY p.dt_data DESC, p.id_pagamento DESC
            """
        )
        lista_pagamentos = cursor.fetchall()
    except Error:
        flash("Erro ao consultar pagamentos no banco de dados.", "danger")
    finally:
        close_db_resources(cursor, connection)

    tipos_pagamento = {
        "C": "Cartao de Credito",
        "D": "Cartao de Debito",
        "P": "Pix",
        "B": "Boleto",
    }

    return render_template(
        "pagamentos.html",
        pagamentos=lista_pagamentos,
        tipos_pagamento=tipos_pagamento,
    )


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=debug_mode)

