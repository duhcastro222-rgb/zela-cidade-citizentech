# Configurações lidas do .env (credenciais fora do código)
import os
from dotenv import load_dotenv

PASTA_PROJETO = os.path.dirname(os.path.abspath(__file__))
PASTA_LOGS = os.path.join(PASTA_PROJETO, "logs")
load_dotenv(os.path.join(PASTA_PROJETO, ".env"), override=True)

OBRIGATORIAS = ["DB_HOST", "DB_PORT", "DB_USER", "DB_NAME", "SECRET_KEY"]

# Chave que assina o cookie de sessão do login (nunca no código)
SECRET_KEY = os.getenv("SECRET_KEY")

# Usuário de demonstração da gestão, criado pelo inicializar_banco.py
ADMIN_USUARIO = os.getenv("ADMIN_USUARIO")
ADMIN_SENHA = os.getenv("ADMIN_SENHA")

MYSQL = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT") or 3306),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME"),
}

# Flask só na máquina local e sem debug
HOST = os.getenv("FLASK_HOST", "127.0.0.1")
PORTA = int(os.getenv("FLASK_PORT") or 5000)
DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"

# Central da prefeitura (servidor TCP)
CENTRAL_HOST = os.getenv("CENTRAL_HOST", "127.0.0.1")
CENTRAL_PORTA = int(os.getenv("CENTRAL_PORTA") or 5050)

# Máximo de chamados por IP a cada minuto
LIMITE_POR_MINUTO = int(os.getenv("LIMITE_POR_MINUTO") or 10)


def validar_configuracao():
    # Devolve as variáveis obrigatórias que faltam no .env
    return [nome for nome in OBRIGATORIAS if not os.getenv(nome)]
