# Rotas REST de chamados: GET, POST, PUT e DELETE
# Públicas: abrir chamado, consultar protocolo e CEP | Gestão (login): o resto
from flask import Blueprint, jsonify, request

import config
from controles import corpo_json, exigir_login, limite_excedido
from modelos import cep_modelo, central_socket, chamado_modelo
from modelos.erros import ErroApi
from modelos.log_modelo import registrar

rotas = Blueprint("chamados", __name__)

envios_por_ip = {}  # anti-spam de chamados


@rotas.get("/api/chamados")
def listar():
    # Gestão: 200 | 401
    exigir_login()
    return jsonify(chamado_modelo.listar())


@rotas.get("/api/chamados/<int:id_chamado>")
def detalhar(id_chamado):
    # Gestão: 200 | 401 | 404
    exigir_login()
    return jsonify(chamado_modelo.buscar(id_chamado))


@rotas.get("/api/chamados/protocolo/<protocolo>")
def acompanhar(protocolo):
    # Público (cidadão): 200 | 400 formato | 404
    return jsonify(chamado_modelo.buscar_por_protocolo(protocolo))


@rotas.get("/api/cep/<cep>")
def consultar_cep(cep):
    # Público: 200 | 400 | 404 | 503
    return jsonify(cep_modelo.buscar_endereco(cep))


@rotas.post("/api/chamados")
def criar():
    # Público: 201 | 400 inválido | 404 CEP inexistente | 429 spam | 503 ViaCEP fora
    if limite_excedido(envios_por_ip, request.remote_addr, config.LIMITE_POR_MINUTO):
        raise ErroApi("Muitos chamados em pouco tempo. Aguarde 1 minuto.", 429)

    dados = corpo_json()
    chamado = chamado_modelo.validar_novo(dados)
    endereco = cep_modelo.buscar_endereco(dados.get("cep"))
    novo = chamado_modelo.criar(chamado, endereco)
    registrar("CRIAR CHAMADO", f"sucesso {novo['protocolo']}")

    # Prioridade alta: avisa a central via socket
    novo["alerta_central"] = None
    if novo["prioridade"] == "alta":
        mensagem = f"{novo['protocolo']} | {novo['tipo']} | {novo['bairro']} - {novo['cidade']}/{novo['uf']}"
        novo["alerta_central"] = central_socket.enviar_alerta(mensagem)
        registrar("ALERTA CENTRAL", "entregue" if novo["alerta_central"] else "central offline")

    # 201 + endereço do recurso criado (boa prática REST)
    return jsonify(novo), 201, {"Location": f"/api/chamados/{novo['id']}"}


@rotas.put("/api/chamados/<int:id_chamado>")
def atualizar(id_chamado):
    # Gestão: 200 | 400 | 401 | 404
    usuario = exigir_login()
    dados = corpo_json()
    if not dados.get("status") and not dados.get("prioridade"):
        raise ErroApi("Informe status e/ou prioridade.")
    chamado = chamado_modelo.atualizar(id_chamado, dados)
    registrar("ATUALIZAR CHAMADO", f"sucesso id={id_chamado} status={chamado['status']} por={usuario}")
    return jsonify(chamado)


@rotas.delete("/api/chamados/<int:id_chamado>")
def remover(id_chamado):
    # Gestão: 200 | 401 | 404
    usuario = exigir_login()
    chamado = chamado_modelo.remover(id_chamado)
    registrar("REMOVER CHAMADO", f"sucesso id={id_chamado} por={usuario}")
    return jsonify({"removido": chamado})
