# CRUD de chamados (MySQL, SQL puro)
# Chamado anônimo: sem nome, CPF, telefone ou e-mail (LGPD - coleta mínima)
import re
import secrets

from modelos.conexao import consultar, executar
from modelos.erros import ErroApi

TIPOS = ["buraco", "iluminacao", "lixo", "calcada", "arvore"]
PRIORIDADES = ["baixa", "media", "alta"]
STATUS = ["aberto", "em_andamento", "resolvido"]


def criar_tabela():
    executar("""
        CREATE TABLE IF NOT EXISTS chamados (
            id INT AUTO_INCREMENT PRIMARY KEY,
            protocolo CHAR(11) NOT NULL UNIQUE,
            tipo VARCHAR(20) NOT NULL,
            descricao VARCHAR(300) NOT NULL,
            referencia VARCHAR(120),
            cep CHAR(8) NOT NULL,
            logradouro VARCHAR(150) NOT NULL,
            bairro VARCHAR(100) NOT NULL,
            cidade VARCHAR(100) NOT NULL,
            uf CHAR(2) NOT NULL,
            latitude DOUBLE,
            longitude DOUBLE,
            prioridade VARCHAR(10) NOT NULL,
            status VARCHAR(15) NOT NULL,
            criado_em DATETIME NOT NULL
        )
    """)


def gerar_protocolo():
    # Aleatório (não sequencial): ninguém adivinha o protocolo de outro cidadão
    return "ZC-" + secrets.token_hex(4).upper()


def formatar(chamado):
    # Data vira texto para o JSON
    chamado["criado_em"] = chamado["criado_em"].strftime("%d/%m/%Y %H:%M")
    return chamado


def validar_opcao(valor, opcoes, campo):
    if valor not in opcoes:
        raise ErroApi(f"{campo} inválido. Use: {', '.join(opcoes)}.")
    return valor


def validar_texto(valor, campo, minimo, maximo):
    valor = str(valor or "").strip()
    if not minimo <= len(valor) <= maximo:
        raise ErroApi(f"{campo} deve ter de {minimo} a {maximo} caracteres.")
    return valor


def validar_coordenada(valor, limite):
    # Opcional; se vier, precisa ser número dentro do limite
    if valor in (None, ""):
        return None
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        raise ErroApi("Localização inválida.")
    if not -limite <= numero <= limite:
        raise ErroApi("Localização inválida.")
    return numero


def validar_novo(dados):
    # Só os campos permitidos passam adiante
    return {
        "tipo": validar_opcao(dados.get("tipo"), TIPOS, "Tipo"),
        "prioridade": validar_opcao(dados.get("prioridade") or "media", PRIORIDADES, "Prioridade"),
        "descricao": validar_texto(dados.get("descricao"), "Descrição", 10, 300),
        "referencia": validar_texto(dados.get("referencia"), "Referência", 0, 120) or None,
        "latitude": validar_coordenada(dados.get("latitude"), 90),
        "longitude": validar_coordenada(dados.get("longitude"), 180),
    }


def listar():
    linhas = consultar("SELECT * FROM chamados ORDER BY id DESC")
    return [formatar(c) for c in linhas]


def buscar(id_chamado):
    linhas = consultar("SELECT * FROM chamados WHERE id = %s", (id_chamado,))
    if not linhas:
        raise ErroApi("Chamado não encontrado.", 404)
    return formatar(linhas[0])


def buscar_por_protocolo(protocolo):
    protocolo = str(protocolo or "").strip().upper()
    if not re.fullmatch(r"ZC-[0-9A-F]{8}", protocolo):
        raise ErroApi("Protocolo inválido. Formato: ZC-XXXXXXXX.")
    linhas = consultar("SELECT * FROM chamados WHERE protocolo = %s", (protocolo,))
    if not linhas:
        raise ErroApi("Protocolo não encontrado.", 404)
    return formatar(linhas[0])


def criar(chamado, endereco):
    _, novo_id = executar(
        "INSERT INTO chamados (protocolo, tipo, descricao, referencia, cep, logradouro, bairro, "
        "cidade, uf, latitude, longitude, prioridade, status, criado_em) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'aberto', NOW())",
        (gerar_protocolo(), chamado["tipo"], chamado["descricao"], chamado["referencia"],
         endereco["cep"], endereco["logradouro"], endereco["bairro"], endereco["cidade"],
         endereco["uf"], chamado["latitude"], chamado["longitude"], chamado["prioridade"]))
    return buscar(novo_id)


def atualizar(id_chamado, dados):
    # O que não vier no corpo mantém o valor atual
    atual = buscar(id_chamado)
    status = validar_opcao(dados.get("status") or atual["status"], STATUS, "Status")
    prioridade = validar_opcao(dados.get("prioridade") or atual["prioridade"], PRIORIDADES, "Prioridade")
    executar("UPDATE chamados SET status = %s, prioridade = %s WHERE id = %s",
             (status, prioridade, id_chamado))
    return buscar(id_chamado)


def remover(id_chamado):
    chamado = buscar(id_chamado)
    executar("DELETE FROM chamados WHERE id = %s", (id_chamado,))
    return chamado
