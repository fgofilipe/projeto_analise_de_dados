import pandas as pd
from sqlalchemy import create_engine, text
from config import DB_CONFIG

CHUNK_SIZE = 1000


def criar_engine():
    url = (
        f"postgresql+psycopg2://"
        f"{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}"
        f"/{DB_CONFIG['database']}"
    )

    return create_engine(url)

def limpar_tabela_silver(engine, tabela, cascade=False):
    comando = f"TRUNCATE TABLE {tabela} RESTART IDENTITY"

    if cascade:
        comando += " CASCADE"

    comando += ";"

    with engine.begin() as conexao:
        conexao.execute(text(comando))

def carregar_ids_viagem_validos(engine):
    df_ids = pd.read_sql(
        "SELECT id_viagem FROM silver_viagem",
        con=engine
    )

    ids_validos = (
        pd.to_numeric(df_ids["id_viagem"], errors="coerce")
        .dropna()
        .astype("int64")
    )

    return set(ids_validos.tolist())

def filtrar_ids_viagem_validos(df, ids_validos, nome_tabela):
    registros_antes = len(df)

    df = df[
        df["id_viagem"].isin(ids_validos)
    ].copy()

    removidos = registros_antes - len(df)

    print(
        f"Registros removidos de {nome_tabela} "
        f"por ausência em silver_viagem: {removidos:,}"
    )

    return df

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
        df[coluna] = (
            df[coluna]
            .astype("string")
            .str.strip()
        )

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
        df[coluna] = converter_decimal(
            df[coluna]
        ).fillna(0)

    df["valor_total"] = (
        df["valor_diarias"]
        + df["valor_passagens"]
        + df["valor_devolucao"]
        + df["valor_outros_gastos"]
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

    df = df.dropna(
        subset=colunas_obrigatorias
    )

    df = df.drop_duplicates(
        subset=["id_viagem"]
    )

    removidos = registros_antes - len(df)

    print(
        f"Registros removidos na limpeza: "
        f"{removidos:,}"
    )
    print(f"Registros preparados: {len(df):,}")

    df = df.where(
        pd.notna(df),
        None
    )

    limpar_tabela_silver(
        engine,
        "silver_viagem",
        cascade=True
    )

    print("Inserindo dados em silver_viagem...")

    df.to_sql(
        name="silver_viagem",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=CHUNK_SIZE,
        method="multi"
    )

    print(
        f"✔ {len(df):,} registros inseridos "
        f"em silver_viagem."
    )


def transformar_pagamento(engine, ids_validos):
    print("\nLendo raw_pagamento...")

    df = pd.read_sql(
        "SELECT * FROM raw_pagamento",
        con=engine
    )

    print(f"{len(df):,} registros encontrados.")

    colunas_texto = [
        "num_proposta",
        "cod_orgao_superior",
        "nome_orgao_superior",
        "cod_orgao_pagador",
        "nome_orgao_pagador",
        "cod_unidade_gestora_pagadora",
        "nome_unidade_gestora_pagadora",
        "tipo_pagamento",
    ]

    for coluna in colunas_texto:
        df[coluna] = (
            df[coluna]
            .astype("string")
            .str.strip()
        )

    df["id_viagem"] = pd.to_numeric(
        df["id_viagem"],
        errors="coerce"
    ).astype("Int64")

    df["valor"] = converter_decimal(
        df["valor"]
    ).fillna(0)

    colunas_obrigatorias = [
        "id_viagem",
        "num_proposta",
        "nome_orgao_superior",
        "nome_orgao_pagador",
        "cod_unidade_gestora_pagadora",
        "nome_unidade_gestora_pagadora",
        "tipo_pagamento",
        "valor",
    ]

    registros_antes = len(df)

    df = df.dropna(
        subset=colunas_obrigatorias
    )

    removidos_nulos = registros_antes - len(df)

    print(
        f"Registros removidos por valores ausentes: "
        f"{removidos_nulos:,}"
    )

    df = filtrar_ids_viagem_validos(
        df,
        ids_validos,
        "silver_pagamento"
    )

    print(f"Registros preparados: {len(df):,}")

    df = df.where(
        pd.notna(df),
        None
    )

    limpar_tabela_silver(
        engine,
        "silver_pagamento"
    )

    print("Inserindo dados em silver_pagamento...")

    df.to_sql(
        name="silver_pagamento",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=CHUNK_SIZE,
        method="multi"
    )

    print(
        f"✔ {len(df):,} registros inseridos "
        f"em silver_pagamento."
    )


def transformar_passagem(engine, ids_validos):
    print("\nLendo raw_passagem...")

    df = pd.read_sql(
        "SELECT * FROM raw_passagem",
        con=engine
    )

    print(f"{len(df):,} registros encontrados.")

    colunas_texto = [
        "num_proposta",
        "meio_transporte",
        "pais_origem_ida",
        "uf_origem_ida",
        "cidade_origem_ida",
        "pais_destino_ida",
        "uf_destino_ida",
        "cidade_destino_ida",
        "pais_origem_volta",
        "uf_origem_volta",
        "cidade_origem_volta",
        "pais_destino_volta",
        "uf_destino_volta",
        "cidade_destino_volta",
    ]

    for coluna in colunas_texto:
        df[coluna] = (
            df[coluna]
            .astype("string")
            .str.strip()
        )

    df["id_viagem"] = pd.to_numeric(
        df["id_viagem"],
        errors="coerce"
    ).astype("Int64")

    df["valor_passagem"] = converter_decimal(
        df["valor_passagem"]
    ).fillna(0)

    df["taxa_servico"] = converter_decimal(
        df["taxa_servico"]
    ).fillna(0)

    df["data_emissao"] = pd.to_datetime(
        df["data_emissao"],
        format="%d/%m/%Y",
        errors="coerce"
    )

    df["hora_emissao"] = pd.to_datetime(
        df["hora_emissao"],
        format="%H:%M",
        errors="coerce"
    ).dt.time

    colunas_obrigatorias = [
        "id_viagem",
        "num_proposta",
        "meio_transporte",
        "pais_origem_ida",
        "cidade_origem_ida",
        "pais_destino_ida",
        "cidade_destino_ida",
        "pais_origem_volta",
        "cidade_origem_volta",
        "pais_destino_volta",
        "cidade_destino_volta",
        "valor_passagem",
        "taxa_servico",
    ]

    registros_antes = len(df)

    df = df.dropna(
        subset=colunas_obrigatorias
    )

    removidos_nulos = registros_antes - len(df)

    print(
        f"Registros removidos por valores ausentes: "
        f"{removidos_nulos:,}"
    )

    df = filtrar_ids_viagem_validos(
        df,
        ids_validos,
        "silver_passagem"
    )

    print(f"Registros preparados: {len(df):,}")

    df = df.where(
        pd.notna(df),
        None
    )

    limpar_tabela_silver(
        engine,
        "silver_passagem"
    )

    print("Inserindo dados em silver_passagem...")

    df.to_sql(
        name="silver_passagem",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=CHUNK_SIZE,
        method="multi"
    )

    print(
        f"✔ {len(df):,} registros inseridos "
        f"em silver_passagem."
    )

def transformar_trecho(engine, ids_validos):
    print("\nLendo raw_trecho...")

    df = pd.read_sql(
        "SELECT * FROM raw_trecho",
        con=engine
    )

    print(f"{len(df):,} registros encontrados.")

    colunas_texto = [
        "num_proposta",
        "origem_pais",
        "origem_uf",
        "origem_cidade",
        "destino_pais",
        "destino_uf",
        "destino_cidade",
        "meio_transporte",
        "missao",
    ]

    for coluna in colunas_texto:
        df[coluna] = (
            df[coluna]
            .astype("string")
            .str.strip()
        )

    df["id_viagem"] = pd.to_numeric(
        df["id_viagem"],
        errors="coerce"
    ).astype("Int64")

    df["sequencia_trecho"] = pd.to_numeric(
        df["sequencia_trecho"],
        errors="coerce"
    ).astype("Int64")

    df["origem_data"] = pd.to_datetime(
        df["origem_data"],
        format="%d/%m/%Y",
        errors="coerce"
    )

    df["destino_data"] = pd.to_datetime(
        df["destino_data"],
        format="%d/%m/%Y",
        errors="coerce"
    )

    df["numero_diarias"] = converter_decimal(
        df["numero_diarias"]
    ).fillna(0)

    df["missao"] = (
        df["missao"]
        .str.upper()
        .replace({
            "SIM": "Sim",
            "NÃO": "Não",
            "NAO": "Não",
        })
    )

    colunas_obrigatorias = [
        "id_viagem",
        "sequencia_trecho",
        "origem_data",
        "destino_data",
        "origem_pais",
        "origem_cidade",
        "destino_pais",
        "destino_cidade",
        "meio_transporte",
        "numero_diarias",
        "missao",
    ]

    registros_antes = len(df)

    df = df.dropna(
        subset=colunas_obrigatorias
    )

    removidos_nulos = registros_antes - len(df)

    print(
        f"Registros removidos por valores ausentes: "
        f"{removidos_nulos:,}"
    )

    df = filtrar_ids_viagem_validos(
        df,
        ids_validos,
        "silver_trecho"
    )

    registros_antes_duplicados = len(df)

    df = df.drop_duplicates(
        subset=[
            "id_viagem",
            "sequencia_trecho",
        ]
    )

    duplicados_removidos = (
        registros_antes_duplicados - len(df)
    )

    print(
        f"Trechos duplicados removidos: "
        f"{duplicados_removidos:,}"
    )
    print(f"Registros preparados: {len(df):,}")

    df = df.where(
        pd.notna(df),
        None
    )

    limpar_tabela_silver(
        engine,
        "silver_trecho"
    )

    print("Inserindo dados em silver_trecho...")

    df.to_sql(
        name="silver_trecho",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=CHUNK_SIZE,
        method="multi"
    )

    print(
        f"✔ {len(df):,} registros inseridos "
        f"em silver_trecho."
    )

def executar_transformacao():
    engine = criar_engine()

    try:
        transformar_viagem(engine)

        ids_validos = carregar_ids_viagem_validos(
            engine
        )

        print(
            f"\nIDs válidos encontrados em silver_viagem: "
            f"{len(ids_validos):,}"
        )

        transformar_pagamento(
            engine,
            ids_validos
        )

        transformar_passagem(
            engine,
            ids_validos
        )

        transformar_trecho(
            engine,
            ids_validos
        )

        print(
            "\nTransformação concluída com sucesso!"
        )

    finally:
        engine.dispose()

if __name__ == "__main__":
    executar_transformacao()