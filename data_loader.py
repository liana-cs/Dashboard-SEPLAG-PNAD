import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = BASE_DIR / "data" / "Tabela1-Renda Total da Forca de Trabalho e Renda total das Famílias Produtoras Por Cnae.xlsx"
SHEET_NAME = "Estatísticas - Agregadas"

def load_data(path: str | Path = DATA_PATH, sheet_name: str = SHEET_NAME) -> pd.DataFrame:
    p = str(path).lower()
    if p.endswith(".xlsx") or p.endswith(".xls"):
        df = pd.read_excel(path, sheet_name=sheet_name)
    else:
        df = pd.read_csv(path, sep=";", decimal=",")

    df.columns = df.columns.str.strip()

    num_cols = [
        "n_ocup_pond",
        "renda_total_pond",
        "Renda Média_Total",
        "n_empregador_pond",
        "renda_empregador_pond",
        "Renda Média_empregador",
        "n_conta_propria_pond",
        "renda_conta_propria_pond",
        "Renda Média_conta_propria",
    ]

    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    if "Ano" in df.columns:
        df["Ano"] = pd.to_numeric(df["Ano"], errors="coerce").astype("Int64")
    if "Trimestre" in df.columns:
        df["Trimestre"] = pd.to_numeric(df["Trimestre"], errors="coerce").astype("Int64")

    df = df[df["Ano"].notna() & df["Trimestre"].notna()].copy()

    if "Renda Média_conta_propria" not in df.columns:
        df["Renda Média_conta_propria"] = df["renda_conta_propria_pond"] / df["n_conta_propria_pond"]
    else:
        if df["Renda Média_conta_propria"].isna().all():
            df["Renda Média_conta_propria"] = df["renda_conta_propria_pond"] / df["n_conta_propria_pond"]

    df["Periodo"] = df["Trimestre"].astype(str) + "T" + df["Ano"].astype(str)
    df = df[df["Periodo"].notna()].copy()
    df = df.sort_values(["Ano", "Trimestre"])

    return df