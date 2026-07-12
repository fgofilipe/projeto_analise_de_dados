import pandas as pd
from sqlalchemy import create_engine, text
from config import DB_CONFIG


def criar_engine():
    url = (
        f"postgresql+psycopg2://"
        f"{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}"
        f"/{DB_CONFIG['database']}"
    )

    return create_engine(url)


def converter_decimal(serie):
    return pd.to_numeric(
        serie
        .astype("string")
        .str.strip()
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False),
        errors="coerce"
    )


def transformar_viagem(engine): 
    print("Lendo raw_viagem...")

    df = pd.read_sql(
        "SELECT * FROM raw_viagem",
        con=engine
    )

    print(f"{len(df):,} registros encontrados.")

    colunas_texto = [
        "num_proposta",
        "situacao",
        "viagem_urgente",
        "justificativa_urgencia",
        "cod_orgao_superior",
        "nome_orgao_superior",
        "cod_orgao_solicitante",
        "nome_orgao_solicitante",
        "cpf_viajante",
        "nome_viajante",
        "cargo",
        "funcao",
        "descricao_funcao",
        "destinos",
        "motivo",
    ]

    for coluna in colunas_texto:
        df[coluna] = df[coluna].astype("string").str.strip()

    df["viagem_urgente"] = (
    df["viagem_urgente"]
    .str.upper()
    .replace({
        "SIM": "Sim",
        "NÃO": "Não",
        "NAO": "Não",
    })
)

    df["id_viagem"] = pd.to_numeric(
        df["id_viagem"],
        errors="coerce"
    ).astype("Int64")

    df["data_inicio"] = pd.to_datetime(
        df["data_inicio"],
        format="%d/%m/%Y",
        errors="coerce"
    )

    df["data_fim"] = pd.to_datetime(
        df["data_fim"],
        format="%d/%m/%Y",
        errors="coerce"
    )

    colunas_valores = [
        "valor_diarias",
        "valor_passagens",
        "valor_devolucao",
        "valor_outros_gastos",
    ]

    for coluna in colunas_valores:
        df[coluna] = converter_decimal(df[coluna]).fillna(0)

    df["valor_total"] = (
        df["valor_diarias"]
        + df["valor_passagens"]
        + df["valor_outros_gastos"]
        - df["valor_devolucao"]
    )

    df["duracao_dias"] = (
        df["data_fim"] - df["data_inicio"]
    ).dt.days

    colunas_obrigatorias = [
        "id_viagem",
        "num_proposta",
        "situacao",
        "viagem_urgente",
        "cod_orgao_superior",
        "nome_orgao_superior",
        "cod_orgao_solicitante",
        "nome_orgao_solicitante",
        "nome_viajante",
        "data_inicio",
        "data_fim",
        "destinos",
        "duracao_dias",
    ]

    registros_antes = len(df)

    df = df.dropna(subset=colunas_obrigatorias)
    df = df.drop_duplicates(subset=["id_viagem"])

    removidos = registros_antes - len(df)

    print(f"Registros removidos na limpeza: {removidos:,}")
    print(f"Registros preparados: {len(df):,}")

    df = df.where(pd.notna(df), None)

    with engine.begin() as conexao:
        conexao.execute(
            text(
                "TRUNCATE TABLE silver_viagem "
                "RESTART IDENTITY CASCADE;"
            )
        )

    print("Inserindo dados em silver_viagem...")

    df.to_sql(
        name="silver_viagem",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=1000,
        method="multi"
    )

    print(f"✔ {len(df):,} registros inseridos em silver_viagem.")


def executar_transformacao():
    engine = criar_engine()

    transformar_viagem(engine)

    print("\nTransformação concluída com sucesso!")

if __name__ == "__main__":
    executar_transformacao()