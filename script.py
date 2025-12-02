import os
from pathlib import Path
import re
import numpy as np
import pandas as pd

# ------------------------------------------------------------
# Configurações
# ------------------------------------------------------------
CAMINHO_BASE = ""  # ajuste
TRIMESTRES = ["01", "02", "03", "04"]        # 2021T1..T4
UF_ALVO = 26                                 # PE

LAYOUT_SAS = "layout_pnad.txt"  # seu layout SAS

# ------------------------------------------------------------
# Parser layout SAS 
# ------------------------------------------------------------
def load_layout_sas(layout_path: str):
    layout_path = Path(layout_path)
    encodings_try = ("utf-8", "ISO-8859-1", "cp1252")
    lines = None
    last_err = None
    for enc in encodings_try:
        try:
            with open(layout_path, "r", encoding=enc) as f:
                lines = f.readlines()
            break
        except UnicodeDecodeError as e:
            last_err = e
            continue
    if lines is None:
        raise UnicodeDecodeError(str(last_err))

    layout = []
    pat = re.compile(r"@\s*(\d+)\s+([A-Za-z0-9_]+)\s+(\$?)(\d+)\.")

    for raw in lines:
        line = raw.strip()
        if "/*" in line:
            line = re.sub(r"/\*.*?\*/", "", line).strip()
        if not line or not line.startswith("@"):
            continue
        m = pat.match(line)
        if m:
            start = int(m.group(1))
            var = m.group(2)
            dollar = m.group(3) == "$"
            width = int(m.group(4))
            layout.append((var, start, width, dollar))
    if not layout:
        raise ValueError("Não foi possível extrair variáveis do layout SAS.")
    return layout

# ------------------------------------------------------------
# Leitura de um trimestre 
# ------------------------------------------------------------
def ler_pnad_trimestre(tri: str, layout, caminho_base: str, uf_alvo: int) -> pd.DataFrame:
    arq = Path(caminho_base) / f"PNADC_{tri}2021.txt"
    print(f"Lendo: {arq}")

    col_names = [v for v, s, w, d in layout]
    colspecs = [(s - 1, s - 1 + w) for _, s, w, _ in layout]

    if not arq.exists():
        print(f"  Arquivo não encontrado: {arq}")
        return pd.DataFrame(columns=col_names)

    df = pd.read_fwf(
        arq,
        colspecs=colspecs,
        names=col_names,
        encoding="ISO-8859-1",
        dtype=str,
        na_values=["", " ", "NA", "NaN"],
    )

    # Converte tudo para numérico onde fizer sentido
    for c in df.columns:
        df[c] = pd.to_numeric(df[c].str.strip(), errors="coerce")

    # Autoescala dos pesos
    for peso in ["V1028", "V1027"]:
        if peso in df.columns:
            mx = df[peso].max(skipna=True)
            if pd.notna(mx) and mx > 1e6:
                df[peso] = df[peso] / 1e8

    # Filtro para PE
    if "UF" in df.columns:
        df_pe = df[df["UF"] == uf_alvo].copy()
    else:
        df_pe = df.copy()

    print(f"  Linhas PE: {len(df_pe)}")
    return df_pe

# ------------------------------------------------------------
# Processar renda e agregações por trimestre 
# ------------------------------------------------------------
def processar_trimestre(df_tri: pd.DataFrame, tri_label: str) -> pd.DataFrame:
    # Precisamos dessas colunas: V403412, V403422, V405112, V405122, V405912, V405922,
    # V1028, V4012, V40161, V4013 (CNAE)
    base = df_tri.copy()

    for col in ["V403412","V403422","V405112","V405122","V405912","V405922","V1028","V4012","V40161","V4013"]:
        if col in base.columns:
            base[col] = pd.to_numeric(base[col], errors="coerce")

    # Renda total do trabalho (igual R)
    base["r_princ"] = np.maximum(base.get("V403412", 0), 0) + np.maximum(base.get("V403422", 0), 0)
    base["r_sec"]   = np.maximum(base.get("V405112", 0), 0) + np.maximum(base.get("V405122", 0), 0)
    base["r_outros"] = np.maximum(base.get("V405912", 0), 0) + np.maximum(base.get("V405922", 0), 0)
    base["renda_total"] = base["r_princ"].fillna(0) + base["r_sec"].fillna(0) + base["r_outros"].fillna(0)

    # Filtra quem tem CNAE (V4013 não nulo)
    base_cnae = base[base["V4013"].notna()].copy()
    base_cnae["CNAE"] = base_cnae["V4013"]

    # Condições (empregador, conta própria)
    cond_empregador = (base_cnae["V4012"] == 5) & (base_cnae["V40161"] == 1)
    cond_conta_propria = (base_cnae["V4012"] == 6)

    # Agregação com apply (um dicionário por grupo)
    def sumariza_grupo(d):
        # cuidado com NaN em V1028
        peso = d["V1028"].fillna(0)
        renda = d["renda_total"].fillna(0)

        # total ocupados
        n_ocup_pond = peso.sum()
        renda_total_pond = (renda * peso).sum()

        # empregadores
        d_emp = d[cond_empregador.loc[d.index]]
        peso_emp = d_emp["V1028"].fillna(0)
        renda_emp = d_emp["renda_total"].fillna(0)
        n_empregador_pond = peso_emp.sum()
        renda_empregador_pond = (renda_emp * peso_emp).sum()

        # conta própria
        d_cp = d[cond_conta_propria.loc[d.index]]
        peso_cp = d_cp["V1028"].fillna(0)
        renda_cp = d_cp["renda_total"].fillna(0)
        n_conta_propria_pond = peso_cp.sum()
        renda_conta_propria_pond = (renda_cp * peso_cp).sum()

        return pd.Series(
            {
                "n_ocup_pond": n_ocup_pond,
                "renda_total_pond": renda_total_pond,
                "n_empregador_pond": n_empregador_pond,
                "renda_empregador_pond": renda_empregador_pond,
                "n_conta_propria_pond": n_conta_propria_pond,
                "renda_conta_propria_pond": renda_conta_propria_pond,
            }
        )

    tabela = base_cnae.groupby("CNAE").apply(sumariza_grupo).reset_index()

    # Rendas médias (com proteção contra divisão por zero)
    tabela["Renda Média_Total"] = tabela["renda_total_pond"] / tabela["n_ocup_pond"].replace({0: np.nan})
    tabela["Renda Média_empregador"] = tabela["renda_empregador_pond"] / tabela["n_empregador_pond"].replace({0: np.nan})
    tabela["Renda Média_conta_propria"] = tabela["renda_conta_propria_pond"] / tabela["n_conta_propria_pond"].replace({0: np.nan})

    # Label do trimestre (ex.: "1T2021", "2T2021", etc.)
    tabela["Trimestre"] = tri_label

    return tabela
# ------------------------------------------------------------
# MAIN: ler todos os trimestres e gerar tabela final
# ------------------------------------------------------------
if __name__ == "__main__":
    layout = load_layout_sas(LAYOUT_SAS)

    tabelas_tris = []

    for tri in TRIMESTRES:
        df_tri = ler_pnad_trimestre(tri, layout, CAMINHO_BASE, UF_ALVO)

        if df_tri.empty:
            continue

        tri_label = f"{int(tri)}T2021"
        tab_tri = processar_trimestre(df_tri, tri_label)
        tabelas_tris.append(tab_tri)

    if not tabelas_tris:
        print("Nenhuma tabela gerada.")
        raise SystemExit

    tabela_final_ponderada = pd.concat(tabelas_tris, ignore_index=True)

    # salvar CSV para backup
    tabela_final_ponderada.to_csv(
        "tabela_final_empregadores_contapropria_ponderada_2021.csv",
        index=False,
        encoding="utf-8"
    )

    # Também salva um Parquet, que usaremos na Dash
    tabela_final_ponderada.to_parquet(
        "tabela_final_empregadores_contapropria_ponderada_2021.parquet",
        index=False
    )

    print("✅ Tabela ponderada final salva.")
    print(tabela_final_ponderada.head())