# Validação da API: confere o código HTTP de cada cenário
# Com o app.py rodando: python testar_api.py
# Pede usuário e senha da gestão (criados com criar_usuario.py)
import os
from getpass import getpass

import requests

import config

URL = f"http://{config.HOST}:{config.PORTA}/api"
CHAMADO = {"tipo": "buraco", "cep": "01310-100", "prioridade": "alta",
           "descricao": "Chamado de teste criado pelo testar_api.py",
           "latitude": -23.5614, "longitude": -46.6559}

usuario = os.getenv("TESTE_USUARIO") or input("Usuário da gestão: ")
senha = os.getenv("TESTE_SENHA") or getpass("Senha: ")

cidadao = requests.Session()  # sem login
gestor = requests.Session()   # guarda o cookie de sessão após o login
falhas = 0


def testar(nome, sessao, metodo, rota, esperado, corpo=None):
    global falhas
    resposta = sessao.request(metodo, URL + rota, json=corpo, timeout=10)
    resultado = "OK" if resposta.status_code == esperado else "FALHOU"
    if resultado == "FALHOU":
        falhas += 1
    print(f"[{resultado}] {nome}: esperado {esperado}, recebido {resposta.status_code}")
    return resposta


# Cidadão (público): abre e consulta pelo protocolo
novo = testar("POST cria chamado", cidadao, "POST", "/chamados", 201, CHAMADO).json()
id_novo, protocolo = novo.get("id"), novo.get("protocolo")
print(f"     protocolo gerado: {protocolo}")
testar("GET por protocolo", cidadao, "GET", f"/chamados/protocolo/{protocolo}", 200)

# Gestão sem login -> 401
testar("GET lista sem login", cidadao, "GET", "/chamados", 401)
testar("PUT sem login", cidadao, "PUT", f"/chamados/{id_novo}", 401, {"status": "resolvido"})
testar("DELETE sem login", cidadao, "DELETE", f"/chamados/{id_novo}", 401)

# Login
testar("Login com senha errada", gestor, "POST", "/login", 401, {"usuario": usuario, "senha": "senha-errada"})
testar("Login vazio", gestor, "POST", "/login", 400, {})
testar("Login correto", gestor, "POST", "/login", 200, {"usuario": usuario, "senha": senha})
testar("Sessão ativa", gestor, "GET", "/sessao", 200)

# CRUD da gestão (logado)
testar("GET lista", gestor, "GET", "/chamados", 200)
testar("GET por id", gestor, "GET", f"/chamados/{id_novo}", 200)
testar("PUT muda status", gestor, "PUT", f"/chamados/{id_novo}", 200, {"status": "em_andamento"})
status = gestor.get(f"{URL}/chamados/{id_novo}", timeout=10).json()["status"]
print(f"     status gravado após PUT: {status} (esperado em_andamento)")
testar("DELETE remove", gestor, "DELETE", f"/chamados/{id_novo}", 200)
testar("GET após DELETE", gestor, "GET", f"/chamados/{id_novo}", 404)

# Recurso inexistente
testar("PUT inexistente", gestor, "PUT", "/chamados/999999", 404, {"status": "resolvido"})
testar("DELETE inexistente", gestor, "DELETE", "/chamados/999999", 404)
testar("Protocolo inexistente", cidadao, "GET", "/chamados/protocolo/ZC-00000000", 404)

# Entrada inválida
testar("Protocolo mal formatado", cidadao, "GET", "/chamados/protocolo/abc", 400)
testar("POST tipo inválido", cidadao, "POST", "/chamados", 400, {**CHAMADO, "tipo": "foguete"})
testar("POST descrição curta", cidadao, "POST", "/chamados", 400, {**CHAMADO, "descricao": "oi"})
testar("POST latitude inválida", cidadao, "POST", "/chamados", 400, {**CHAMADO, "latitude": 200})
testar("POST CEP com letras", cidadao, "POST", "/chamados", 400, {**CHAMADO, "cep": "abc"})
testar("POST CEP inexistente", cidadao, "POST", "/chamados", 404, {**CHAMADO, "cep": "99999999"})
testar("PUT status inválido", gestor, "PUT", "/chamados/1", 400, {"status": "apagado"})
testar("PUT corpo vazio", gestor, "PUT", "/chamados/1", 400, {})
testar("GET CEP (ViaCEP)", cidadao, "GET", "/cep/01310100", 200)

# SQL Injection na descrição é gravado como texto comum (tabela continua intacta)
ataque = {**CHAMADO, "prioridade": "baixa", "descricao": "x'); DROP TABLE chamados; --"}
id_ataque = testar("POST com SQL Injection", cidadao, "POST", "/chamados", 201, ataque).json().get("id")
testar("GET tabela intacta", gestor, "GET", "/chamados", 200)
gestor.delete(f"{URL}/chamados/{id_ataque}", timeout=10)

# Logout encerra a sessão
testar("Logout", gestor, "POST", "/logout", 200)
testar("GET lista após logout", gestor, "GET", "/chamados", 401)

# Anti-spam: acima do limite por minuto -> 429
for _ in range(config.LIMITE_POR_MINUTO):
    cidadao.post(URL + "/chamados", json={}, timeout=10)
testar("POST acima do limite", cidadao, "POST", "/chamados", 429, CHAMADO)

# Força bruta no login: acima de 5 tentativas por minuto -> 429
for _ in range(5):
    cidadao.post(URL + "/login", json={"usuario": "x", "senha": "y"}, timeout=10)
testar("Login acima do limite", cidadao, "POST", "/login", 429, {"usuario": "x", "senha": "y"})

print(f"\n{'Todos os testes passaram.' if falhas == 0 else f'{falhas} teste(s) falharam.'}")
