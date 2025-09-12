#!/bin/env python3
import pandas as pd
import os

from teste_internet import dir_resultados
from config import SSIDS, CONTRATADO_DOWNLOAD, CONTRATADO_UPLOAD


def compara_anatel_df(df, contratado_dl, contratado_ul):
    """Gera relatório por dataset com as métricas exigidas pela Anatel."""
    # Garantir que as colunas existem
    required = {"Download_Mbps", "Upload_Mbps", "Ping_ms"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Faltam colunas no DataFrame: {missing}")

    # Cálculos Download
    media_dl = df["Download_Mbps"].mean()
    perc40_dl = (df["Download_Mbps"] >= 0.40 * contratado_dl).mean() * 100

    # Cálculos Upload
    media_ul = df["Upload_Mbps"].mean()
    perc40_ul = (df["Upload_Mbps"] >= 0.40 * contratado_ul).mean() * 100

    # Cálculos Ping
    media_ping = df["Ping_ms"].mean()

    # Monta tabela com linhas = Métrica (Download/Upload/Ping)
    tabela = pd.DataFrame(
        {
            "Média (% do contratado)": [
                (media_dl / contratado_dl) * 100 if contratado_dl > 0 else float("nan"),
                (media_ul / contratado_ul) * 100 if contratado_ul > 0 else float("nan"),
                float("nan"),
            ],
            "Cumpre média (≥80%)": [
                media_dl >= 0.80 * contratado_dl if contratado_dl > 0 else False,
                media_ul >= 0.80 * contratado_ul if contratado_ul > 0 else False,
                pd.NA,
            ],
            "Testes ≥40% (%)": [
                perc40_dl,
                perc40_ul,
                float("nan"),
            ],
            "Cumpre instantâneo (≥95%)": [
                perc40_dl >= 95,
                perc40_ul >= 95,
                pd.NA,
            ],
            "Média (ms)": [
                float("nan"),
                float("nan"),
                media_ping,
            ],
            "Cumpre latência (≤80ms)": [
                pd.NA,
                pd.NA,
                media_ping <= 80 if pd.notna(media_ping) else pd.NA,
            ],
        },
        index=["Download", "Upload", "Ping"],
    )
    return tabela

# Exemplo: gerando o comparativo lado a lado

relatorios = dict()
for ssid in SSIDS:
    print(ssid)
    df = pd.read_csv(os.path.join(dir_resultados, f"resultados_speedtest_{ssid}.csv"))
    df = df[(df["Download_Mbps"] != 0) & (df["Upload_Mbps"] != 0)]
    relatorios[ssid] = compara_anatel_df(df, CONTRATADO_DOWNLOAD, CONTRATADO_UPLOAD)

comparativo = pd.concat(relatorios, axis=1)

# (Opcional) Formatar percentuais com 1 casa e Booleanos como "Sim/Não"
def formatar_exibicao(df):
    fmt = df.copy()
    for ds in ["Castro1", "Castro2"]:
        # Percentuais
        for col in ["Média (% do contratado)", "Testes ≥40% (%)"]:
            if (ds, col) in fmt.columns:
                fmt[(ds, col)] = fmt[(ds, col)].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "")
        # Booleans
        for col in ["Cumpre média (≥80%)", "Cumpre instantâneo (≥95%)", "Cumpre latência (≤80ms)"]:
            if (ds, col) in fmt.columns:
                fmt[(ds, col)] = fmt[(ds, col)].map({True: "Sim", False: "Não", pd.NA: ""})
        # Ping médio
        if (ds, "Média (ms)") in fmt.columns:
            fmt[(ds, "Média (ms)")] = fmt[(ds, "Média (ms)")]\
                .apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")
    return fmt

comparativo_formatado = formatar_exibicao(comparativo)

print("\n=== Comparativo ANATEL (2.4Ghz vs 5Ghz) ===")
with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print(comparativo_formatado)

# (Opcional) Exportar para Excel com múltiplos cabeçalhos
# comparativo_formatado.to_excel("comparativo_anatel.xlsx", merge_cells=False)

