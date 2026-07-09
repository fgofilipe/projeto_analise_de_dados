import pandas as pd
from pathlib import Path

PASTA_RAW = Path("data/raw")

arquivos = [
    "2025_Viagem.csv",
    "2025_Pagamento.csv",
    "2025_Passagem.csv",
    "2025_Trecho.csv",
]

for arquivo in arquivos:
    caminho = PASTA_RAW / arquivo

    print("\n" + "=" * 80)
    print(f"ARQUIVO: {arquivo}")
    print("=" * 80)

    df = pd.read_csv(caminho, sep=";", encoding="latin1")

    print(f"Linhas: {df.shape[0]}")
    print(f"Colunas: {df.shape[1]}")

    print("\nColunas:")
    print(df.columns.tolist())

    print("\nPrimeiras linhas:")
    print(df.head())

    print("\nValores nulos por coluna:")
    print(df.isnull().sum())