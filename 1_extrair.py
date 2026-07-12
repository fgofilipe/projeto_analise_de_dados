from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text
from config import DB_CONFIG, MAPEAMENTOS_RAW


BASE_DIR = Path(__file__).resolve().parent
PASTA_RAW = BASE_DIR / "data" / "raw"

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

def criar_engine():

    url = (
        f"postgresql+psycopg2://"
        f"{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}"
        f"/{DB_CONFIG['database']}"
    )
    return create_engine(url)

def limpar_tabelas_raw(engine):
    tabelas = [
        "raw_pagamento",
        "raw_passagem",
        "raw_trecho",
        "raw_viagem",
    ]

    with engine.begin() as conexao:
        for tabela in tabelas:
            conexao.execute(text(f"TRUNCATE TABLE {tabela};"))

    print("Tabelas Raw limpas.")

def carregar_csv(nome_arquivo):

    caminho = PASTA_RAW / nome_arquivo

    print(f"\nLendo {nome_arquivo}...")

    df = pd.read_csv(
        caminho,
        sep=";",
        encoding="latin1",
        dtype=str
    )

    df.columns = df.columns.str.strip()
    print(f"{len(df):,} registros encontrados.")

    return df

def preparar_dataframe(nome_base, df):

    df.rename(
        columns=MAPEAMENTOS_RAW[nome_base],
        inplace=True
    )

    return df

def inserir_raw(engine, df, tabela):

    print(f"Inserindo em {tabela}...")
    
    df.to_sql(
        name=tabela,
        con=engine,
        if_exists="append",
        index=False,
        chunksize=10000,
        method="multi"
    )

    print(f"✔ {len(df):,} registros inseridos.")

def executar_extracao():

    engine = criar_engine()

    limpar_tabelas_raw(engine)

    for nome_base, nome_arquivo in ARQUIVOS.items():

        df = carregar_csv(nome_arquivo)
        df = preparar_dataframe(nome_base, df)

        inserir_raw(
            engine,
            df,
            TABELAS_RAW[nome_base]
        )

    print("\nExtração finalizada com sucesso!")

if __name__ == "__main__":
    executar_extracao()