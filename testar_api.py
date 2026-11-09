# Validação da API: confere o código HTTP de cada cenário
# Com o app.py rodando: python testar_api.py
import requests

import config

URL = f"http://{config.HOST}:{config.PORTA}/api"
CHAMADO = {"tipo": "buraco", "cep": "01310-100", "prioridade": "alta",
           "descricao": "Chamado de teste criado pelo testar_api.py"}


def testar(nome, metodo, rota, esperado, corpo=None):
    resposta = requests.request(metodo, URL + rota, json=corpo, timeout=10)
    resultado = "OK" if resposta.status_code == esperado else "FALHOU"
    print(f"[{resultado}] {nome}: esperado {esperado}, recebido {resposta.status_code}")
    return resposta


# CRUD completo
id_novo = testar("POST cria chamado", "POST", "/chamados", 201, CHAMADO).json().get("id")
testar("GET lista", "GET", "/chamados", 200)
testar("GET por id", "GET", f"/chamados/{id_novo}", 200)
testar("PUT muda status", "PUT", f"/chamados/{id_novo}", 200, {"status": "em_andamento"})
testar("DELETE remove", "DELETE", f"/chamados/{id_novo}", 200)

# Recurso inexistente
testar("GET inexistente", "GET", "/chamados/999999", 404)
testar("PUT inexistente", "PUT", "/chamados/999999", 404, {"status": "resolvido"})
testar("DELETE inexistente", "DELETE", "/chamados/999999", 404)

# Entrada inválida
testar("POST tipo inválido", "POST", "/chamados", 400, {**CHAMADO, "tipo": "foguete"})
testar("POST descrição curta", "POST", "/chamados", 400, {**CHAMADO, "descricao": "oi"})
testar("POST CEP com letras", "POST", "/chamados", 400, {**CHAMADO, "cep": "abc"})
testar("POST CEP inexistente", "POST", "/chamados", 404, {**CHAMADO, "cep": "99999999"})
testar("PUT status inválido", "PUT", "/chamados/1", 400, {"status": "apagado"})
testar("PUT corpo vazio", "PUT", "/chamados/1", 400, {})

# SQL Injection na descrição é gravado como texto comum (tabela continua intacta)
ataque = {**CHAMADO, "prioridade": "baixa", "descricao": "x'); DROP TABLE chamados; --"}
id_ataque = testar("POST com SQL Injection", "POST", "/chamados", 201, ataque).json().get("id")
testar("GET tabela intacta", "GET", "/chamados", 200)
requests.delete(f"{URL}/chamados/{id_ataque}", timeout=10)

# Anti-spam: acima do limite por minuto -> 429
for _ in range(config.LIMITE_POR_MINUTO):
    requests.post(URL + "/chamados", json={}, timeout=10)
testar("POST acima do limite", "POST", "/chamados", 429, CHAMADO)
