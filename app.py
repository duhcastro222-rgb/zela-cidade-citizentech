# Zela Cidade - chamados de zeladoria urbana
# MVC: modelos/ (dados e serviços), visao/ (tela), controles/ (rotas /api)
from flask import Flask

import config
from controles import chamados_controle
from controles.erros import registrar_erros
from modelos import chamado_modelo, conexao
from modelos.log_modelo import registrar

app = Flask(__name__, static_folder="visao", static_url_path="")
app.json.ensure_ascii = False
app.json.sort_keys = False
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024  # corpo acima de 16 KB -> 413

app.register_blueprint(chamados_controle.rotas)
registrar_erros(app)


@app.get("/")
def inicio():
    return app.send_static_file("index.html")


def preparar_banco():
    # Só sobe o servidor com .env completo e MySQL respondendo
    faltando = config.validar_configuracao()
    if faltando:
        print(f"[ERRO] Faltam no .env: {', '.join(faltando)}")
        return False
    try:
        conexao.conectar().close()
    except Exception as erro:
        print(f"[ERRO] MySQL: {erro}")
        return False
    chamado_modelo.criar_tabela()
    return True


if __name__ == "__main__":
    if not preparar_banco():
        exit(1)
    registrar("SERVIDOR", f"iniciado em {config.HOST}:{config.PORTA}")
    app.run(host=config.HOST, port=config.PORTA, debug=config.DEBUG)
