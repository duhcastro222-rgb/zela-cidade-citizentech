# Fonte externa: ViaCEP (gratuita, sem chave) completa o endereço pelo CEP
import re

import requests

from modelos.erros import ErroApi


def buscar_endereco(cep):
    cep = re.sub(r"\D", "", str(cep or ""))  # mantém só os dígitos
    if len(cep) != 8:
        raise ErroApi("CEP inválido. Use 8 números (ex.: 01310-100).")

    try:
        resposta = requests.get(f"https://viacep.com.br/ws/{cep}/json/", timeout=5)
        resposta.raise_for_status()
        dados = resposta.json()
    except (requests.exceptions.RequestException, ValueError):
        raise ErroApi("Serviço de CEP indisponível. Tente novamente.", 503)

    # CEP inexistente volta como {"erro": "true"}
    if "erro" in dados:
        raise ErroApi("CEP não encontrado.", 404)

    return {
        "cep": cep,
        "logradouro": dados.get("logradouro") or "",
        "bairro": dados.get("bairro") or "",
        "cidade": dados.get("localidade") or "",
        "uf": dados.get("uf") or "",
    }
