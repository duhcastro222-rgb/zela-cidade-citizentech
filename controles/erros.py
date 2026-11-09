# Todo erro vira {"erro": "mensagem"} com o código HTTP certo.
# Detalhes técnicos ficam só no terminal do servidor.
import mysql.connector
from flask import jsonify, request
from werkzeug.exceptions import HTTPException

from modelos.erros import ErroApi
from modelos.log_modelo import registrar


def registrar_erros(app):

    @app.errorhandler(ErroApi)
    def erro_regra(erro):
        registrar(f"{request.method} {request.path}", f"erro {erro.status}")
        return jsonify({"erro": erro.mensagem}), erro.status

    @app.errorhandler(mysql.connector.Error)
    def erro_banco(erro):
        app.logger.error(f"MySQL: {erro}")
        registrar(f"{request.method} {request.path}", "erro 503 banco")
        return jsonify({"erro": "Banco de dados indisponível."}), 503

    @app.errorhandler(HTTPException)
    def erro_http(erro):
        # 404 rota, 405 método, 413 corpo grande
        if request.path.startswith("/api/"):
            return jsonify({"erro": erro.name}), erro.code
        return erro

    @app.errorhandler(Exception)
    def erro_inesperado(erro):
        app.logger.exception("Erro inesperado")
        registrar(f"{request.method} {request.path}", "erro 500")
        return jsonify({"erro": "Erro interno no servidor."}), 500
