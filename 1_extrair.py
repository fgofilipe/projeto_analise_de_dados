from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

from config import DB_CONFIG, MAPEAMENTOS_RAW


# ==========================================================
# CAMINHOS
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent
PASTA_RAW = BASE_DIR / "data" / "raw"


# ==========================================================
# ARQUIVOS
# ==========================================================

ARQUIVOS = {
    "viagem": "2025_Viagem.csv",
    "pagamento": "2025_Pagamento.csv",
    "passagem": "2025_Passagem.csv",
    "trecho": "2025_Trecho.csv",
}


TABELAS_RAW = {
    "viagem": "raw_viagem",
    "pagamento": "raw_pagamento",
    "passagem": "raw_passagem",
    "trecho": "raw_trecho",
}


# ==========================================================
# CONEXÃO
# ==========================================================

def criar_engine():

    usuario = DB_CONFIG["user"]
    senha = DB_CONFIG["password"]
    host = DB_CONFIG["host"]
    porta = DB_CONFIG["port"]
    banco = DB_CONFIG["database"]

    url = (
        f"postgresql+psycopg2://"
        f"{usuario}:{senha}@{host}:{porta}/{banco}"
    )

    return create_engine(url)


# ==========================================================
# LEITURA DOS CSVs
# ==========================================================

def carregar_csv(nome_arquivo):

    caminho = PASTA_RAW / nome_arquivo

    print(f"\nLendo arquivo: {nome_arquivo}")

    df = pd.read_csv(
        caminho,
        sep=";",
        encoding="latin1",
        dtype=str
    )

    # Remove espaços no início/fim do nome das colunas
    df.columns = df.columns.str.strip()

    print(f"Registros encontrados: {len(df):,}")

    return df


# ==========================================================
# RENOMEIA AS COLUNAS
# ==========================================================

def preparar_dataframe(nome_tabela, df):

    print("Renomeando colunas...")

    df.rename(
        columns=MAPEAMENTOS_RAW[nome_tabela],
        inplace=True
    )

    return df


# ==========================================================
# INSERE NA RAW
# ==========================================================

def inserir_raw(engine, df, tabela):

    print(f"Inserindo dados em {tabela}...")

    df.to_sql(
        name=tabela,
        con=engine,
        if_exists="append",
        index=False,
        chunksize=10000,
        method="multi"
    )

    print(f"✔ {len(df):,} registros inseridos.")


# ==========================================================
# EXECUÇÃO
# ==========================================================

def executar():

    engine = criar_engine()

    for nome, arquivo in ARQUIVOS.items():

        tabela = TABELAS_RAW[nome]

        df = carregar_csv(arquivo)

        df = preparar_dataframe(nome, df)

        inserir_raw(engine, df, tabela)

    print("\n=========================================")
    print("EXTRAÇÃO FINALIZADA COM SUCESSO!")
    print("=========================================")


if __name__ == "__main__":
    executar()