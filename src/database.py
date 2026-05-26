import mysql.connector
import os

# Configuracao principal da conexao.
# Altere estes valores de acordo com seu ambiente local.
host = os.getenv("DB_HOST", "localhost")
port = int(os.getenv("DB_PORT", "3306"))
user = os.getenv("DB_USER", "root")
password = os.getenv("DB_PASSWORD", "password")
database = os.getenv("DB_NAME", "LOCADORA_CARROS")


def get_connection():
    """
    Retorna uma conexao MySQL usando mysql-connector-python.
    Lanca excecao em caso de falha para o app tratar.
    """
    return mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
    )
