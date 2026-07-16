import sys
import zipfile
from pathlib import Path

import gdown
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from config import DB_CONFIG, DRIVE_FILE_ID, MAPEAMENTOS_RAW

#_______________________________________________________________#

BASE_DIR = Path(__file__).resolve().parent
PASTA_DATA = BASE_DIR / "data"
PASTA_RAW = PASTA_DATA / "raw"
CAMINHO_ZIP = PASTA_DATA / "Viagens_2025_6meses.zip"

CHUNK_SIZE_CSV = 50000
CHUNK_SIZE_BANCO = 10000

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


def baixar_zip():
    if not DRIVE_FILE_ID:
        raise ValueError(
            "DRIVE_FILE_ID não foi configurado no arquivo .env."
        )

    PASTA_DATA.mkdir(parents=True, exist_ok=True)
    PASTA_RAW.mkdir(parents=True, exist_ok=True)

    if CAMINHO_ZIP.exists():
        CAMINHO_ZIP.unlink()

    print("Baixando arquivo ZIP do Google Drive...")

    url = f"https://drive.google.com/uc?id={DRIVE_FILE_ID}"

    resultado = gdown.download(
        url=url,
        output=str(CAMINHO_ZIP),
        quiet=False
        )

    if resultado is None or not CAMINHO_ZIP.exists():
        raise RuntimeError(
            "O download do arquivo ZIP não foi concluído."
        )

    print("Download concluído.")


def extrair_zip():
    print("Extraindo arquivos...")

    for arquivo in PASTA_RAW.glob("*.csv"):
        arquivo.unlink()

    try:
        with zipfile.ZipFile(CAMINHO_ZIP, "r") as arquivo_zip:
            arquivo_zip.extractall(PASTA_RAW)

    except zipfile.BadZipFile as erro:
        raise RuntimeError(
            "O arquivo baixado não é um ZIP válido."
        ) from erro

    finally:
        if CAMINHO_ZIP.exists():
            CAMINHO_ZIP.unlink()

    print("Extração concluída.")


def validar_arquivos():
    arquivos_ausentes = []

    for nome_arquivo in ARQUIVOS.values():
        caminho = PASTA_RAW / nome_arquivo

        if not caminho.exists():
            arquivos_ausentes.append(nome_arquivo)

    if arquivos_ausentes:
        raise FileNotFoundError(
            "Arquivos CSV não encontrados: "
            + ", ".join(arquivos_ausentes)
        )

    print("Os quatro arquivos CSV foram encontrados.")


def limpar_tabelas_raw(engine):
    with engine.begin() as conexao:
        for tabela in TABELAS_RAW.values():
            conexao.execute(
                text(f"TRUNCATE TABLE {tabela};")
            )

    print("Tabelas Raw limpas.")


def carregar_csv(nome_arquivo):
    caminho = PASTA_RAW / nome_arquivo

    print(f"\nLendo {nome_arquivo}...")

    partes = pd.read_csv(
        caminho,
        sep=";",
        encoding="latin1",
        dtype=str,
        chunksize=CHUNK_SIZE_CSV
    )

    df = pd.concat(partes, ignore_index=True)
    df.columns = df.columns.str.strip()

    print(f"{len(df):,} registros encontrados.")

    return df


def preparar_dataframe(nome_base, df):
    df = df.rename(
        columns=MAPEAMENTOS_RAW[nome_base]
    )

    colunas_esperadas = list(
        MAPEAMENTOS_RAW[nome_base].values()
    )

    colunas_ausentes = [
        coluna
        for coluna in colunas_esperadas
        if coluna not in df.columns
    ]

    if colunas_ausentes:
        raise ValueError(
            f"Colunas ausentes em {nome_base}: "
            f"{colunas_ausentes}"
        )

    return df[colunas_esperadas]


def inserir_raw(engine, df, tabela):
    print(f"Inserindo dados em {tabela}...")

    df.to_sql(
        name=tabela,
        con=engine,
        if_exists="append",
        index=False,
        chunksize=CHUNK_SIZE_BANCO,
        method="multi"
    )

    print(
        f"{len(df):,} registros inseridos em {tabela}."
    )


def executar_extracao():
    engine = None

    try:
        baixar_zip()
        extrair_zip()
        validar_arquivos()

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

        print(
            "\nExtração automatizada e carga Raw "
            "finalizadas com sucesso!"
        )

    except FileNotFoundError as erro:
        print(f"\nErro de arquivo: {erro}")
        sys.exit(1)

    except (ValueError, RuntimeError) as erro:
        print(f"\nErro de download ou validação: {erro}")
        sys.exit(1)

    except SQLAlchemyError as erro:
        print(f"\nErro ao acessar o PostgreSQL: {erro}")
        sys.exit(1)

    except Exception as erro:
        print(f"\nErro inesperado na extração: {erro}")
        sys.exit(1)

    finally:
        if engine is not None:
            engine.dispose()


if __name__ == "__main__":
    executar_extracao()