# Usuários da prefeitura que podem acessar a gestão
# A senha nunca é gravada: só o hash (werkzeug, com salt)
from werkzeug.security import check_password_hash, generate_password_hash

from modelos.conexao import consultar, executar
from modelos.erros import ErroApi


def criar_tabela():
    executar("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario VARCHAR(50) NOT NULL UNIQUE,
            senha_hash VARCHAR(255) NOT NULL
        )
    """)


def criar(usuario, senha):
    if len(senha) < 8:
        raise ErroApi("A senha deve ter pelo menos 8 caracteres.")
    if consultar("SELECT id FROM usuarios WHERE usuario = %s", (usuario,)):
        raise ErroApi("Usuário já existe.", 409)
    executar("INSERT INTO usuarios (usuario, senha_hash) VALUES (%s, %s)",
             (usuario, generate_password_hash(senha)))


def autenticar(usuario, senha):
    # True se o usuário existe e a senha confere com o hash
    linhas = consultar("SELECT senha_hash FROM usuarios WHERE usuario = %s", (usuario,))
    return bool(linhas) and check_password_hash(linhas[0]["senha_hash"], senha)
