# Central da prefeitura: servidor TCP que recebe alertas de prioridade alta
# Rodar em outro terminal: python servidor_central.py
import os
import socket
from datetime import datetime

import config

ARQUIVO_LOG = os.path.join(config.PASTA_LOGS, "central.log")


def gravar_log(mensagem):
    os.makedirs(config.PASTA_LOGS, exist_ok=True)
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    with open(ARQUIVO_LOG, "a", encoding="utf-8") as arquivo:
        arquivo.write(f"[{data_hora}] {mensagem}\n")


servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    servidor.bind((config.CENTRAL_HOST, config.CENTRAL_PORTA))
    servidor.listen(5)
    servidor.settimeout(1)  # permite encerrar com Ctrl+C no Windows
    print(f"Central ouvindo em {config.CENTRAL_HOST}:{config.CENTRAL_PORTA}")

    while True:
        try:
            conexao, endereco = servidor.accept()
        except socket.timeout:
            continue
        try:
            conexao.settimeout(5)
            mensagem = conexao.recv(512).decode("utf-8", errors="replace").strip()  # limite de 512 bytes
            if mensagem:
                print(f"[ALERTA] {mensagem}")
                gravar_log(mensagem)
                conexao.sendall(b"OK")
        except socket.error as erro:
            print(f"Erro com {endereco[0]}: {erro}")
        finally:
            conexao.close()

except KeyboardInterrupt:
    print("Central encerrada.")
except socket.error as erro:
    print(f"Erro de socket: {erro}")
finally:
    servidor.close()
