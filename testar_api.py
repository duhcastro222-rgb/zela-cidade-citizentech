# Validação da API: confere o código HTTP de cada cenário
# Com o app.py rodando: python testar_api.py
import requests

import config

URL = f"http://{config.HOST}:{config.PORTA}/api"
CHAMADO = {"tipo": "buraco", "cep": "01310-100", "prioridade": "alta",
           "descricao": "Chamado de teste criado pelo testar_api.py",
           "latitude": -23.5614, "longitude": -46.6559}
falhas = 0


def testar(nome, metodo, rota, esperado, corpo=None):
    global falhas
    resposta = requests.request(metodo, URL + rota, json=corpo, timeout=10)
    resultado = "OK" if resposta.status_code == esperado else "FALHOU"
    if resultado == "FALHOU":
        falhas += 1
    print(f"[{resultado}] {nome}: esperado {esperado}, recebido {resposta.status_code}")
    return resposta


# CRUD completo
novo = testar("POST cria chamado", "POST", "/chamados", 201, CHAMADO).json()
id_novo, protocolo = novo.get("id"), novo.get("protocolo")
print(f"     protocolo gerado: {protocolo}")
testar("GET lista", "GET", "/chamados", 200)
testar("GET por id", "GET", f"/chamados/{id_novo}", 200)
testar("GET por protocolo", "GET", f"/chamados/protocolo/{protocolo}", 200)
testar("PUT muda status", "PUT", f"/chamados/{id_novo}", 200, {"status": "em_andamento"})
status = requests.get(f"{URL}/chamados/{id_novo}", timeout=10).json()["status"]
print(f"     status gravado após PUT: {status} (esperado em_andamento)")
testar("DELETE remove", "DELETE", f"/chamados/{id_novo}", 200)
testar("GET após DELETE", "GET", f"/chamados/{id_novo}", 404)

# Recurso inexistente
testar("PUT inexistente", "PUT", "/chamados/999999", 404, {"status": "resolvido"})
testar("DELETE inexistente", "DELETE", "/chamados/999999", 404)
testar("Protocolo inexistente", "GET", "/chamados/protocolo/ZC-00000000", 404)

# Entrada inválida
testar("Protocolo mal formatado", "GET", "/chamados/protocolo/abc", 400)
testar("POST tipo inválido", "POST", "/chamados", 400, {**CHAMADO, "tipo": "foguete"})
testar("POST descrição curta", "POST", "/chamados", 400, {**CHAMADO, "descricao": "oi"})
testar("POST latitude inválida", "POST", "/chamados", 400, {**CHAMADO, "latitude": 200})
testar("POST CEP com letras", "POST", "/chamados", 400, {**CHAMADO, "cep": "abc"})
testar("POST CEP inexistente", "POST", "/chamados", 404, {**CHAMADO, "cep": "99999999"})
testar("PUT status inválido", "PUT", "/chamados/1", 400, {"status": "apagado"})
testar("PUT corpo vazio", "PUT", "/chamados/1", 400, {})
testar("GET CEP (ViaCEP)", "GET", "/cep/01310100", 200)

# SQL Injection na descrição é gravado como texto comum (tabela continua intacta)
ataque = {**CHAMADO, "prioridade": "baixa", "descricao": "x'); DROP TABLE chamados; --"}
id_ataque = testar("POST com SQL Injection", "POST", "/chamados", 201, ataque).json().get("id")
testar("GET tabela intacta", "GET", "/chamados", 200)
requests.delete(f"{URL}/chamados/{id_ataque}", timeout=10)

# Anti-spam: acima do limite por minuto -> 429
for _ in range(config.LIMITE_POR_MINUTO):
    requests.post(URL + "/chamados", json={}, timeout=10)
testar("POST acima do limite", "POST", "/chamados", 429, CHAMADO)

print(f"\n{'Todos os testes passaram.' if falhas == 0 else f'{falhas} teste(s) falharam.'}")
