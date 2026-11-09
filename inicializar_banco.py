# Cria o banco e a tabela e insere chamados fictícios (só se estiver vazia)
import mysql.connector

import config
from modelos import chamado_modelo, usuario_modelo
from modelos.conexao import consultar, executar

# Dados fictícios com CEPs públicos
# (tipo, descrição, referência, cep, logradouro, bairro, cidade, uf, latitude, longitude, prioridade)
EXEMPLOS = [
    ("buraco", "Buraco grande na faixa da direita, carros desviando para a contramão.",
     "Em frente ao ponto de ônibus", "01310100", "Avenida Paulista", "Bela Vista", "São Paulo", "SP",
     -23.5614, -46.6559, "alta"),
    ("iluminacao", "Três postes apagados seguidos, rua muito escura à noite.",
     "Perto da praça", "04538133", "Avenida Brigadeiro Faria Lima", "Itaim Bibi", "São Paulo", "SP",
     -23.5868, -46.6823, "media"),
    ("lixo", "Lixo acumulado na calçada há mais de uma semana.",
     None, "20040020", "Avenida Rio Branco", "Centro", "Rio de Janeiro", "RJ",
     -22.9035, -43.1772, "media"),
    ("calcada", "Calçada quebrada, cadeirante não consegue passar.",
     "Esquina com a padaria", "30130010", "Praça Sete de Setembro", "Centro", "Belo Horizonte", "MG",
     -19.9191, -43.9386, "baixa"),
]

faltando = config.validar_configuracao()
if faltando:
    exit(f"[ERRO] Faltam no .env: {', '.join(faltando)}")

# Nome de banco não aceita %s, então é validado antes
nome_banco = config.MYSQL["database"]
if not nome_banco.replace("_", "").isalnum():
    exit("[ERRO] DB_NAME inválido (use letras, números e _).")

dados_conexao = dict(config.MYSQL)
del dados_conexao["database"]  # o banco pode ainda não existir
conexao = mysql.connector.connect(**dados_conexao)
conexao.cursor().execute(f"CREATE DATABASE IF NOT EXISTS {nome_banco}")
conexao.close()

chamado_modelo.criar_tabela()
usuario_modelo.criar_tabela()
print(f"[OK] Banco '{nome_banco}' e tabelas 'chamados' e 'usuarios' prontos.")

# Usuário da gestão vindo do .env (senha gravada só como hash)
if config.ADMIN_USUARIO and config.ADMIN_SENHA:
    if consultar("SELECT id FROM usuarios WHERE usuario = %s", (config.ADMIN_USUARIO,)):
        print(f"[INFO] Usuário '{config.ADMIN_USUARIO}' já existe.")
    else:
        usuario_modelo.criar(config.ADMIN_USUARIO, config.ADMIN_SENHA)
        print(f"[OK] Usuário '{config.ADMIN_USUARIO}' criado para a gestão.")

if consultar("SELECT COUNT(*) AS total FROM chamados")[0]["total"] == 0:
    for exemplo in EXEMPLOS:
        executar(
            "INSERT INTO chamados (protocolo, tipo, descricao, referencia, cep, logradouro, bairro, "
            "cidade, uf, latitude, longitude, prioridade, status, criado_em) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'aberto', NOW())",
            (chamado_modelo.gerar_protocolo(),) + exemplo)
    print(f"[OK] {len(EXEMPLOS)} chamados fictícios inseridos.")
