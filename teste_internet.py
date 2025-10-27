#!/bin/env python3
import csv
import os
import time #modificado
import datetime
import subprocess
from typing import Optional, Tuple
import speedtest  # pip install speedtest-cli
import subprocess
from typing import Optional
from sys import platform


# Verifica se o arquivo config.py está presente
try:
    from config import SSIDS
except ImportError:
    print("Erro: O arquivo 'config.py' não foi encontrado ou está incompleto.")
    print("Por favor, verifique se o arquivo existe e contém a lista SSIDS.")
    exit(1)

# Importa o intervalo do config.py
from config import intervalo_segundos 

parent_dir = os.path.dirname(os.path.abspath(__file__))
dir_resultados = os.path.join(parent_dir, "resultados")
os.makedirs(dir_resultados, exist_ok=True)

# ==== CONFIG ====


# Configurações específicas para Windows

interface_name = "Wi-Fi"  # ajuste se sua interface tiver outro nome
check_interval = 1    # segundos entre checagens de status
connect_timeout = 10    # segundos para esperar conexão após o comando connect
pause_between = 2    # pausa entre disconnect e connect

NETWORKS = [
    {
    "ssid": ssid,
    "csv": os.path.join(dir_resultados, f"resultados_speedtest_{ssid}.csv")
    } for ssid in SSIDS
]

##---- FUNÇÕES ----

### Conecta ao SSID usando netsh (Windows) ou nmcli (Linux) ###

def connect_wifi(ssid: str, password: Optional[str] = None) -> bool:
    """Conecta ao SSID no Windows (netsh) ou Linux (nmcli).
    Assume que perfis já estão salvos no sistema quando for o Windows.
    """
    try:
        if platform.startswith("win") or platform == "win32":
            # tenta desconectar antes
            subprocess.run(['netsh', 'wlan', 'disconnect'], capture_output=True, text=True)
            interface = interface_name
            p = subprocess.run(['netsh', 'wlan', 'connect', f'name={ssid}', f'ssid={ssid}', f'interface={interface}'], capture_output=True, text=True)
            if p.returncode != 0:
                print(f"[ERRO] netsh connect {ssid}: {p.stdout} {p.stderr}")
                return False
            # aguarda confirmação
            deadline = time.time() + connect_timeout
            while time.time() < deadline:
                s = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], capture_output=True, text=True)
                out = s.stdout or s.stderr or ''
                state = None
                current_ssid = None
                for line in out.splitlines():
                    if ':' in line:
                        key, val = line.split(':', 1)
                        key = key.strip()
                        val = val.strip()
                        if key.lower() in ('state', 'estado'):
                            state = val.lower()
                        if key == 'SSID':
                            current_ssid = val
                if state and (('connected' in state) or ('conectado' in state)) and current_ssid == ssid:
                    return True
                time.sleep(check_interval)
            print(f"[ERRO] Timeout ao conectar {ssid}")
            return False
        else:
            # Linux (nmcli)
            subprocess.run(['nmcli', 'device', 'wifi', 'rescan'], capture_output=True, text=True)
            cmd = ['nmcli', 'device', 'wifi', 'connect', ssid]
            if password:
                cmd += ['password', password]
            p = subprocess.run(cmd, capture_output=True, text=True)
            if p.returncode != 0:
                print(f"[ERRO] nmcli connect {ssid}: {p.stdout} {p.stderr}")
                return False
            return True
    except Exception as e:
        print(f"[ERRO] Exceção ao conectar {ssid}: {e}")
        return False
    

### Roda o speedtest e retorna download, upload e ping ###
def speedtest_run() -> Tuple[float, float, float]:
    st = speedtest.Speedtest(secure = True)
    st.get_best_server()
    download = st.download() / 1_000_000
    upload = st.upload() / 1_000_000
    ping = st.results.ping
    return download, upload, ping


### Adiciona os resultados ao CSV ###
def append_csv(csv_path: str, ssid: str, download: float, upload: float, ping: float):
    header = ["DataHora", "SSID", "Download_Mbps", "Upload_Mbps", "Ping_ms"]
    new_file = not os.path.isfile(csv_path)
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(header)
        datahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        w.writerow([datahora, ssid, f"{download:.2f}", f"{upload:.2f}", f"{ping:.2f}"])

def run_cmd(cmd_list) -> subprocess.CompletedProcess:
    return subprocess.run(cmd_list, capture_output=True, text=True)


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

        print("Testando apenas a rede atual....")
        print(platform)
        print("Conectado. Rodando speedtest…")
        try:
            down, up, ping = speedtest_run()
            append_csv(csv_path, ssid, down, up, ping)
            print(f"[OK] {ssid} → Down {down:.2f} Mbps | Up {up:.2f} Mbps | Ping {ping:.2f} ms")
        except Exception as e:
            print(f"[ERRO] Speedtest em '{ssid}': {e}")




if __name__ == "__main__":
    try:
        while True:
            main()
            print(f"Aguardando {intervalo_segundos} segundos até a próxima execução...")
            time.sleep(intervalo_segundos)
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário. Saindo...")