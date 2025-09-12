#!/bin/env python
import pandas as pd
import os

from teste_internet import dir_resultados, SSIDS


# Lê os datasets

def resumo_legivel(df, nome):
    print(f"\n=== Resultados para {nome} === Contagem: {len(df)}")
    df = df.tail(100)
    for coluna in df.select_dtypes(include=["float64", "int64"]).columns:
        print(f"{coluna}->\tMédia: {df[coluna].mean():.2f}\tMínimo: {df[coluna].min():.2f}\tMáximo: {df[coluna].max():.2f}")


# Exibir os dois resumos
mensagem = "=== Estatísticas relacionadas às últimas 100 medições ==="
print()
print(len(mensagem) * "=")
print(mensagem)
print(len(mensagem) * "=")

ultimas_observacoes = []
for ssid in SSIDS:
    df = pd.read_csv(os.path.join(dir_resultados, f"resultados_speedtest_{ssid}.csv"))
    df = df[(df["Download_Mbps"] != 0) & (df["Upload_Mbps"] != 0)]
    resumo_legivel(df, ssid)
    ultimas_observacoes.append(df.tail(1))


print("\n\n")
mensagem = "===Últimas medições==="
print(len(mensagem) * "=")
print(mensagem)
print(len(mensagem) * "=")
print(pd.concat(ultimas_observacoes))
