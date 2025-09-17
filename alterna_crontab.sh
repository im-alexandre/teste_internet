#!/bin/bash
# -*- coding: utf-8 -*-
if [ "$(id -u)" -ne 0 ]; then
    exec sudo "$0" "$@"
fi

# Linha alvo (ajuste o caminho se necessário)
TARGET="python3 /opt/teste_internet/teste_internet.py"

# Exporta crontab atual
crontab -l > /tmp/crontab.tmp 2>/dev/null

if grep -q "$TARGET" /tmp/crontab.tmp; then
    # Se já está comentada, descomenta
    if grep -q "^#.*$TARGET" /tmp/crontab.tmp; then
        sed -i "s|^#\(.*$TARGET\)|\1|" /tmp/crontab.tmp
        echo "✔ Linha descomentada"
    else
        # Se está ativa, comenta
        sed -i "s|^\(.*$TARGET\)|#\1|" /tmp/crontab.tmp
	echo "# Linha comentada"
    fi
else
    echo "⚠ Linha não encontrada na crontab"
fi

# Reaplica a crontab
crontab /tmp/crontab.tmp
