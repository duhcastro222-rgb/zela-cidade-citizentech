# Controle: rotas Flask que validam a entrada, chamam o modelo e devolvem JSON
#   /api/chamados -> CRUD no MySQL | /api/cep -> ViaCEP | /api/login -> sessão
import time

from flask import request, session

from modelos.erros import ErroApi


def corpo_json():
    # Lê o JSON da requisição ou responde 400
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        raise ErroApi("O corpo da requisição deve ser um JSON válido.")
    return dados


def exigir_login():
    # Rotas da gestão: sem sessão -> 401
    if "usuario" not in session:
        raise ErroApi("Faça login para acessar a gestão.", 401)
    return session["usuario"]


def limite_excedido(registro, ip, limite):
    # Conta os envios do IP no último minuto; True se passou do limite
    agora = time.time()
    recentes = [t for t in registro.get(ip, []) if agora - t < 60]
    registro[ip] = recentes
    if len(recentes) >= limite:
        return True
    recentes.append(agora)
    return False
