# Rotas REST de chamados: GET, POST, PUT e DELETE
import time

from flask import Blueprint, jsonify, request

import config
from controles import corpo_json
from modelos import cep_modelo, central_socket, chamado_modelo
from modelos.erros import ErroApi
from modelos.log_modelo import registrar

rotas = Blueprint("chamados", __name__)

envios_por_ip = {}  # {ip: [horários dos envios no último minuto]}


def limite_excedido(ip):
    # Anti-spam: barra o IP que passar de LIMITE_POR_MINUTO envios
    agora = time.time()
    recentes = [t for t in envios_por_ip.get(ip, []) if agora - t < 60]
    envios_por_ip[ip] = recentes
    if len(recentes) >= config.LIMITE_POR_MINUTO:
        return True
    recentes.append(agora)
    return False


@rotas.get("/api/chamados")
def listar():
    # 200
    return jsonify(chamado_modelo.listar())


@rotas.get("/api/chamados/<int:id_chamado>")
def detalhar(id_chamado):
    # 200 | 404
    return jsonify(chamado_modelo.buscar(id_chamado))


@rotas.post("/api/chamados")
def criar():
    # 201 | 400 inválido | 404 CEP inexistente | 429 spam | 503 ViaCEP fora
    if limite_excedido(request.remote_addr):
        raise ErroApi("Muitos chamados em pouco tempo. Aguarde 1 minuto.", 429)

    dados = corpo_json()
    chamado = chamado_modelo.validar_novo(dados)
    endereco = cep_modelo.buscar_endereco(dados.get("cep"))
    novo = chamado_modelo.criar(chamado, endereco)
    registrar("CRIAR CHAMADO", f"sucesso id={novo['id']}")

    # Prioridade alta: avisa a central via socket
    novo["alerta_central"] = None
    if novo["prioridade"] == "alta":
        mensagem = f"Chamado {novo['id']} | {novo['tipo']} | {novo['bairro']} - {novo['cidade']}/{novo['uf']}"
        novo["alerta_central"] = central_socket.enviar_alerta(mensagem)
        registrar("ALERTA CENTRAL", "entregue" if novo["alerta_central"] else "central offline")

    return jsonify(novo), 201


@rotas.put("/api/chamados/<int:id_chamado>")
def atualizar(id_chamado):
    # 200 | 400 | 404
    dados = corpo_json()
    if not dados.get("status") and not dados.get("prioridade"):
        raise ErroApi("Informe status e/ou prioridade.")
    chamado = chamado_modelo.atualizar(id_chamado, dados)
    registrar("ATUALIZAR CHAMADO", f"sucesso id={id_chamado} status={chamado['status']}")
    return jsonify(chamado)


@rotas.delete("/api/chamados/<int:id_chamado>")
def remover(id_chamado):
    # 200 | 404
    chamado = chamado_modelo.remover(id_chamado)
    registrar("REMOVER CHAMADO", f"sucesso id={id_chamado}")
    return jsonify({"removido": chamado})
