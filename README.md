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
 
### UTILIZAÇÃO:
* o script `teste_internet.py` faz o teste utilizando a biblioteca do speedtest
* o script `resumo.py` traz algumas estatísticas descritivas e a última observação de cada rede
* o script `comparacao_anatel.py` verifica se as medições estão de acordo com os parâmetros impostos pela anatel de acordo com o contrato

## TODO: 
* Adicionar funcionalidades para windows
* Alterar para incluir as senhas no arquivo `config.py` ou em um `.env`

