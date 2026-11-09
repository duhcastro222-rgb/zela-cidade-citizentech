# Rotas de login da gestão (sessão do Flask)
from flask import Blueprint, jsonify, request, session

from controles import corpo_json, exigir_login, limite_excedido
from modelos import usuario_modelo
from modelos.erros import ErroApi
from modelos.log_modelo import registrar

rotas = Blueprint("login", __name__)

tentativas_por_ip = {}  # anti força bruta


@rotas.post("/api/login")
def login():
    # 200 | 400 | 401 usuário ou senha errados | 429 tentativas demais
    if limite_excedido(tentativas_por_ip, request.remote_addr, 5):
        raise ErroApi("Muitas tentativas. Aguarde 1 minuto.", 429)
    dados = corpo_json()
    usuario = str(dados.get("usuario") or "").strip()
    senha = str(dados.get("senha") or "")
    if not usuario or not senha:
        raise ErroApi("Informe usuário e senha.")

    if not usuario_modelo.autenticar(usuario, senha):
        registrar("LOGIN", "falha")  # não grava o que foi digitado
        raise ErroApi("Usuário ou senha inválidos.", 401)  # não diz qual dos dois errou

    session.clear()
    session["usuario"] = usuario
    registrar("LOGIN", f"sucesso usuario={usuario}")
    return jsonify({"usuario": usuario})


@rotas.post("/api/logout")
def logout():
    registrar("LOGOUT", f"usuario={session.get('usuario')}")
    session.clear()
    return jsonify({"mensagem": "Sessão encerrada."})


@rotas.get("/api/sessao")
def sessao():
    # A tela de gestão pergunta se ainda está logada: 200 | 401
    return jsonify({"usuario": exigir_login()})
