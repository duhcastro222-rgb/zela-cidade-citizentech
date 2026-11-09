# Cadastra um usuário autorizado a acessar a gestão
# Uso: python criar_usuario.py  (a senha é digitada sem aparecer na tela)
from getpass import getpass

from modelos import usuario_modelo
from modelos.erros import ErroApi

usuario_modelo.criar_tabela()

usuario = input("Usuário: ").strip()
senha = getpass("Senha (mínimo 8 caracteres): ")

if not usuario or len(usuario) > 50:
    exit("[ERRO] Usuário deve ter de 1 a 50 caracteres.")
if senha != getpass("Confirme a senha: "):
    exit("[ERRO] As senhas não conferem.")

try:
    usuario_modelo.criar(usuario, senha)
    print(f"[OK] Usuário '{usuario}' criado.")
except ErroApi as erro:
    print(f"[ERRO] {erro.mensagem}")
