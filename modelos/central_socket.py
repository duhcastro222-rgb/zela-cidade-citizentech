# Cliente TCP: envia alerta para a central da prefeitura (servidor_central.py)
import socket

import config


def enviar_alerta(mensagem):
    # True se a central confirmou; False se estiver fora (o chamado já foi salvo)
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.settimeout(3)
    try:
        cliente.connect((config.CENTRAL_HOST, config.CENTRAL_PORTA))
        cliente.sendall(mensagem.encode("utf-8"))
        return cliente.recv(16) == b"OK"
    except OSError:
        return False
    finally:
        cliente.close()
