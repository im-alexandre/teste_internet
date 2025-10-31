SSIDS = ["SSID1", "SSID2"]

csv = "C:/path/para/o/csv"
template = "./template_reclamacao.j2"
out = "reclamacao.txt"
cliente = "Nome do cliente"
cpf = "CPF DO CLIENTE"
cidade = "CIDADE DO CLIENTE"
uf = "SUA UF"
contrato = "Número do contrato"
operadora = "Sua operadora"
email = "email do cliente"
telefone = "telefone para contato"
plano_down = 350
plano_up = 35
limiar_inst_pct = 40.0
limiar_med_pct = 80.0
frequencia_desc = "a cada 2 minutos"
ferramenta = "speedtest-cli + python"
protocolos_anteriores = []
top_n_ocorrencias = 5
tecnologia = "Fixa"

# >>> Ajuste aqui as velocidades contratadas <<<
CONTRATADO_DOWNLOAD = plano_down  # Mbps
CONTRATADO_UPLOAD = plano_up  # Mbps
