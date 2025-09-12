# Script para teste de internet

## Preparação:
### CERTIFIQUE-SE DE QUE AS REDES JÁ ESTÃO CONECTADAS NO SEU DISPOSITIVO DISPENSANDO O USO DE SENHA

### INSTALAÇÃO DE DEPENDÊNCIAS
```sh
pip install -r requirements.txt
```

## CONFIGURAÇÃO
* Renomear o arquivo `config_sample.py` para `config.py`
* Altere a variável `SSID` em `config.py` com a lista de redes que você quer testar
* Altere os valores contratados por meio das variáveis `CONTRATADO_DOWNLOAD` e `CONTRATADO_UPLOAD`.
    * Normalmente o upload é 10% do Download

## TODO: 
* Adicionar funcionalidades para windows
* Alterar para incluir as senhas no arquivo `config.py` ou em um `.env`

