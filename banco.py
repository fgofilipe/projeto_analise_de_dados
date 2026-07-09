import psycopg2
from config import DB_CONFIG


def conectar():
    """Cria e retorna uma conexão com o PostgreSQL."""
    return psycopg2.connect(**DB_CONFIG)


def testar_conexao():
    """Testa a conexão com o banco de dados."""
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        cursor.execute("SELECT version();")
        versao = cursor.fetchone()

        print("Conexão com o PostgreSQL realizada com sucesso!")
        print(f"Versão do banco: {versao[0]}")

        cursor.close()
        conexao.close()

    except Exception as erro:
        print("Erro ao conectar ao PostgreSQL:")
        print(erro)


if __name__ == "__main__":
    testar_conexao()