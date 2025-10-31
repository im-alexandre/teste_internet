#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Renderiza um texto de reclamação usando um template Jinja2 a partir de um CSV de medições.
Requisitos: pandas, jinja2
"""

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape

import config


def main():
    csv_path = Path(config.csv)
    if not csv_path.exists():
        print(f"CSV não encontrado: {csv_path}", file=sys.stderr)
        sys.exit(1)

    # Esperado: colunas padrão (ajuste conforme seu arquivo):
    # DataHora,Download_Mbps,Upload_Mbps,Ping_ms
    df = pd.read_csv(csv_path)
    # Inferir DataHora
    if "DataHora" not in df.columns:
        raise ValueError("CSV precisa ter uma coluna 'DataHora'")
    df["DataHora"] = pd.to_datetime(df["DataHora"], errors="coerce")
    df = df.dropna(subset=["DataHora"]).sort_values("DataHora").reset_index(drop=True)

    "DataHora,SSID,Download_Mbps,Upload_Mbps,Ping_ms"
    # Garantir colunas numéricas com defaults quando ausentes
    for col, default in [
        ("Download_Mbps", 0.0),
        ("Upload_Mbps", 0.0),
        ("Ping_ms", None),
    ]:
        if col not in df.columns:
            df[col] = default
    num_cols = ["Download_Mbps", "Upload_Mbps", "Ping_ms"]
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df[num_cols] = df[num_cols].fillna(0.0)

    # Período
    periodo_inicio = df["DataHora"].min()
    periodo_fim = df["DataHora"].max()
    dias_monitorados = max(
        1, (periodo_fim.normalize() - periodo_inicio.normalize()).days + 1
    )

    # Estatísticas básicas
    total = len(df)
    media_down = df["Download_Mbps"].mean() if total else 0.0
    media_up = df["Upload_Mbps"].mean() if total else 0.0
    media_ping = df["Ping_ms"].mean() if total else 0.0

    # Piores medições (down e up)
    idx_pior_down = df["Download_Mbps"].idxmin()
    pior_down = df.loc[idx_pior_down, "Download_Mbps"] if total else 0.0
    pior_down_ts = df.loc[idx_pior_down, "DataHora"] if total else None

    idx_pior_up = df["Upload_Mbps"].idxmin()
    pior_up = df.loc[idx_pior_up, "Upload_Mbps"] if total else 0.0
    pior_up_ts = df.loc[idx_pior_up, "DataHora"] if total else None

    # Conformidade vs contratado
    lim_inst_down = config.plano_down * (config.limiar_inst_pct / 100.0)
    lim_inst_up = config.plano_up * (config.limiar_inst_pct / 100.0)

    qtd_abaixo_inst_down = int((df["Download_Mbps"] < lim_inst_down).sum())
    qtd_abaixo_inst_up = int((df["Upload_Mbps"] < lim_inst_up).sum())
    pct_abaixo_inst_down = (
        round((qtd_abaixo_inst_down / total) * 100.0, 2) if total else 0.0
    )
    pct_abaixo_inst_up = (
        round((qtd_abaixo_inst_up / total) * 100.0, 2) if total else 0.0
    )

    pct_media_down_contrato = (
        round((media_down / config.plano_down) * 100.0, 2) if config.plano_down else 0.0
    )
    pct_media_up_contrato = (
        round((media_up / config.plano_up) * 100.0, 2) if config.plano_up else 0.0
    )

    # Indisponibilidade: sequência de leituras com down ~ 0 ou perda alta
    # Ajuste o critério conforme sua realidade
    down_zero_thresh = 0.5  # Mbps
    indisponiveis = df["Download_Mbps"] <= down_zero_thresh

    # Estimar maior duração contínua em minutos considerando cadência média
    if total >= 2:
        # cadência média (minutos) entre amostras
        deltas = df["DataHora"].diff().dropna().dt.total_seconds() / 60.0
        passo_medio_min = max(1.0, deltas.median())
    else:
        passo_medio_min = 1.0

    maior_indisp_min = 0.0
    qtd_janelas_indisp = 0
    corrente = 0
    for flag in indisponiveis:
        if flag:
            corrente += 1
        else:
            if corrente > 0:
                qtd_janelas_indisp += 1
                maior_indisp_min = max(maior_indisp_min, corrente * passo_medio_min)
                corrente = 0
    if corrente > 0:
        qtd_janelas_indisp += 1
        maior_indisp_min = max(maior_indisp_min, corrente * passo_medio_min)

    # Selecionar ocorrências representativas (piores downloads)
    ocorrencias = df.nsmallest(config.top_n_ocorrencias, "Download_Mbps")[
        ["DataHora", "Download_Mbps", "Upload_Mbps", "Ping_ms"]
    ].copy()
    ocorrencias["DataHora"] = ocorrencias["DataHora"].dt.strftime("%Y-%m-%d %H:%M:%S")
    ocorrencias_representativas = ocorrencias.to_dict(orient="records")

    # Preparar contexto
    hoje = datetime.now().strftime("%d/%m/%Y")
    context = dict(
        hoje=hoje,
        operadora=config.operadora,
        tecnologia=config.tecnologia,
        cliente_nome=config.cliente,
        cidade=config.cidade,
        uf=config.uf,
        plano_Download_Mbps=round(config.plano_down, 2),
        plano_Upload_Mbps=round(config.plano_up, 2),
        periodo_inicio=periodo_inicio.strftime("%d/%m/%Y %H:%M:%S")
        if pd.notna(periodo_inicio)
        else "n/d",
        periodo_fim=periodo_fim.strftime("%d/%m/%Y %H:%M:%S")
        if pd.notna(periodo_fim)
        else "n/d",
        dias_monitorados=int(dias_monitorados),
        total_medicoes=int(total),
        media_Download_Mbps=round(media_down, 2),
        media_Upload_Mbps=round(media_up, 2),
        pior_Download_Mbps=round(pior_down, 2),
        pior_down_ts=pior_down_ts.strftime("%d/%m/%Y %H:%M:%S")
        if pior_down_ts is not None
        else "n/d",
        pior_Upload_Mbps=round(pior_up, 2),
        pior_up_ts=pior_up_ts.strftime("%d/%m/%Y %H:%M:%S")
        if pior_up_ts is not None
        else "n/d",
        media_Ping_ms=round(media_ping, 1),
        limiar_instantaneo_down_pct=config.limiar_inst_pct,
        limiar_instantaneo_up_pct=config.limiar_inst_pct,
        limiar_medio_pct=config.limiar_med_pct,
        qtd_abaixo_inst_down=int(qtd_abaixo_inst_down),
        qtd_abaixo_inst_up=int(qtd_abaixo_inst_up),
        pct_abaixo_inst_down=pct_abaixo_inst_down,
        pct_abaixo_inst_up=pct_abaixo_inst_up,
        pct_media_down_contrato=pct_media_down_contrato,
        pct_media_up_contrato=pct_media_up_contrato,
        qtd_janelas_indisp=int(qtd_janelas_indisp),
        maior_indisp_min=int(round(maior_indisp_min)),
        ocorrencias_representativas=ocorrencias_representativas,
        email=config.email,
        telefone=config.telefone,
        frequencia_coleta_desc=config.frequencia_desc,
        ferramenta=config.ferramenta,
        template=config.template,
        cpf=config.cpf,
    )

    # Render
    env = Environment(
        loader=FileSystemLoader(Path(config.template).parent),
        autoescape=select_autoescape(enabled_extensions=(), default_for_string=False),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(Path(config.template).name)
    rendered = template.render(**context)

    out_path = Path(config.out)
    out_path.write_text(rendered, encoding="utf-8")
    print(f"OK: arquivo gerado em {out_path.resolve()}")


if __name__ == "__main__":
    main()
