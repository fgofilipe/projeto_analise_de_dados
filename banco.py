import psycopg2
from config import DB_CONFIG


def conectar():
    """Cria e retorna uma conexão com o PostgreSQL."""
    return psycopg2.connect(**DB_CONFIG)


def testar_conexao():
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor()

        cursor.execute("SELECT version();")
        versao = cursor.fetchone()

        print("Conexão com o PostgreSQL realizada com sucesso!")
        print(f"Versão do banco: {versao[0]}")

    except Exception as erro:
        print("Erro ao conectar ao PostgreSQL:")
        print(erro)

    finally:
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()