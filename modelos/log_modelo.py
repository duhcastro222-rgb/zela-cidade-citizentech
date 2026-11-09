# Log em arquivo: data/hora, ação e resultado (sem dados digitados pelo cidadão)
import os
from datetime import datetime

import config

ARQUIVO_LOG = os.path.join(config.PASTA_LOGS, "app.log")


def registrar(acao, resultado):
    os.makedirs(config.PASTA_LOGS, exist_ok=True)
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    with open(ARQUIVO_LOG, "a", encoding="utf-8") as arquivo:
        arquivo.write(f"[{data_hora}] {acao} | {resultado}\n")
