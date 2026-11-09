# Acesso ao MySQL sem ORM
import mysql.connector

import config


def conectar():
    return mysql.connector.connect(**config.MYSQL)


def consultar(sql, parametros=()):
    # SELECT -> lista de dicionários
    # prepared=True envia SQL e valores separados (evita SQL Injection)
    conexao = conectar()
    try:
        cursor = conexao.cursor(prepared=True, dictionary=True)
        cursor.execute(sql, parametros)
        return cursor.fetchall()
    finally:
        conexao.close()


def executar(sql, parametros=()):
    # INSERT/UPDATE/DELETE -> (linhas afetadas, id gerado)
    conexao = conectar()
    try:
        cursor = conexao.cursor(prepared=True)
        cursor.execute(sql, parametros)
        conexao.commit()
        return cursor.rowcount, cursor.lastrowid
    finally:
        conexao.close()
