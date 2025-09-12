#!/bin/env python3
import csv
import os
import datetime
import subprocess
from typing import Optional, Tuple
import speedtest  # pip install speedtest-cli
import subprocess
from typing import Optional

from config import SSIDS


parent_dir = os.path.dirname(os.path.abspath(__file__))
dir_resultados = os.path.join(parent_dir, "resultados")
os.makedirs(dir_resultados, exist_ok=True)

# ===================== CONFIG =====================



NETWORKS = [
    {
        "ssid": ssid,
        "csv": os.path.join(dir_resultados, f"resultados_speedtest_{ssid}.csv")
    } for ssid in SSIDS
]


def connect_wifi(ssid: str, password: Optional[str] = None) -> bool:
    try:
        varrer = ["nmcli", "dev", "wifi", "rescan"]
        run(varrer)
        listar = ["nmcli", "dev", "wifi", "list"]
        run(listar)
        conectar = ["nmcli", "dev", "wifi", "connect", ssid]
        if password:
            conectar += ["password", password]
        run(conectar)
        return True

    except subprocess.CalledProcessError as e:
        print(f"[ERRO] Falha ao conectar {ssid}: {e}")
        return False


def speedtest_run() -> Tuple[float, float, float]:
    st = speedtest.Speedtest(secure = True)
    st.get_best_server()
    download = st.download() / 1_000_000
    upload = st.upload() / 1_000_000
    ping = st.results.ping
    return download, upload, ping


def append_csv(csv_path: str, ssid: str, download: float, upload: float, ping: float):
    header = ["DataHora", "SSID", "Download_Mbps", "Upload_Mbps", "Ping_ms"]
    new_file = not os.path.isfile(csv_path)
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(header)
        datahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        w.writerow([datahora, ssid, f"{download:.2f}", f"{upload:.2f}", f"{ping:.2f}"])


def run(cmd, check=True):
    return subprocess.run(cmd, check=check, capture_output=True)


def main():
    for net in NETWORKS:
        ssid = net["ssid"]
        password = net.get('password')
        csv_path = net["csv"]

        print(f"\n=== Conectando em '{ssid}' ===")
        ok_cmd = connect_wifi(ssid, password)
        if not ok_cmd:
            print("não conectou")
            continue

        print("Conectado. Rodando speedtest…")
        try:
            down, up, ping = speedtest_run()
            append_csv(csv_path, ssid, down, up, ping)
            print(f"[OK] {ssid} → Down {down:.2f} Mbps | Up {up:.2f} Mbps | Ping {ping:.2f} ms")
        except Exception as e:
            print(f"[ERRO] Speedtest em '{ssid}': {e}")


if __name__ == "__main__":
    main()
