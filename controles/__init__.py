# Controle: rotas Flask que validam a entrada, chamam o modelo e devolvem JSON
#   /api/chamados -> CRUD no MySQL | /api/cep -> ViaCEP
from flask import request

from modelos.erros import ErroApi


def corpo_json():
    # Lê o JSON da requisição ou responde 400
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        raise ErroApi("O corpo da requisição deve ser um JSON válido.")
    return dados
