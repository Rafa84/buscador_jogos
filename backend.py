# backend.py

import requests
import time
import json
from datetime import datetime
import sqlite3

DB_FILE = "historico_de_precos.db"

def setup_database():
    """Cria o banco de dados e as tabelas necessárias se não existirem."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Tabela para os jogos que estamos monitorando
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jogos_monitorados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        )
    ''')
    # Tabela para guardar todo o histórico de preços encontrados
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historico_precos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_jogo_monitorado INTEGER,
            nome_item TEXT NOT NULL,
            preco REAL NOT NULL,
            loja TEXT NOT NULL,
            link TEXT,
            validade_oferta TEXT,
            data_consulta TEXT NOT NULL,
            FOREIGN KEY (id_jogo_monitorado) REFERENCES jogos_monitorados (id)
        )
    ''')
    conn.commit()
    conn.close()

def adicionar_novo_jogo(nome_jogo):
    """Adiciona um novo jogo à tabela de monitoramento."""
    if not nome_jogo:
        return "Nome do jogo não pode ser vazio."
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO jogos_monitorados (nome) VALUES (?)", (nome_jogo,))
        conn.commit()
        return f"'{nome_jogo}' adicionado com sucesso!"
    except sqlite3.IntegrityError:
        return f"'{nome_jogo}' já está na lista de monitoramento."
    finally:
        conn.close()

def obter_jogos_monitorados():
    """Retorna uma lista de todos os jogos sendo monitorados."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM jogos_monitorados ORDER BY nome")
    jogos = cursor.fetchall()
    conn.close()
    return jogos

def buscar_e_salvar_precos(API_KEY, PAIS):
    """Busca os preços atuais para todos os jogos monitorados e salva no histórico."""
    conn_main = sqlite3.connect(DB_FILE)
    cursor_main = conn_main.cursor()
    cursor_main.execute("SELECT id, nome FROM jogos_monitorados")
    jogos_para_verificar = cursor_main.fetchall()
    conn_main.close()
    
    if not jogos_para_verificar:
        yield "Nenhum jogo para verificar. Adicione um jogo primeiro."
        return

    yield f"Verificando {len(jogos_para_verificar)} jogo(s)..."
    
    for id_monitorado, nome_jogo in jogos_para_verificar:
        yield f"\nBuscando por '{nome_jogo}'..."
        
        try:
            # Busca jogos e DLCs
            url_busca = f"https://api.isthereanydeal.com/games/search/v1?key={API_KEY}&title={nome_jogo}&results=50"
            resposta_busca = requests.get(url_busca).json()
            
            if not resposta_busca:
                yield f"-> Nenhum item encontrado para '{nome_jogo}'."
                continue
            
            # Obtém preços
            ids_api = [jogo['id'] for jogo in resposta_busca]
            url_precos = f"https://api.isthereanydeal.com/games/prices/v3?key={API_KEY}&country={PAIS}"
            lista_de_precos = requests.post(url_precos, json=ids_api).json()
            precos_por_id = {item['id']: item for item in lista_de_precos}

            conn_write = sqlite3.connect(DB_FILE)
            cursor_write = conn_write.cursor()
            
            ofertas_encontradas = 0
            for jogo_encontrado in resposta_busca:
                if jogo_encontrado['id'] in precos_por_id and precos_por_id[jogo_encontrado['id']]['deals']:
                    oferta = min(precos_por_id[jogo_encontrado['id']]['deals'], key=lambda x: x['price']['amount'])
                    validade = "N/A"
                    if oferta['expiry']:
                        validade = datetime.fromisoformat(oferta['expiry']).strftime('%d/%m/%Y')
                    
                    cursor_write.execute('INSERT INTO historico_precos (id_jogo_monitorado, nome_item, preco, loja, link, validade_oferta, data_consulta) VALUES (?, ?, ?, ?, ?, ?, ?)',
                                   (id_monitorado, jogo_encontrado['title'], oferta['price']['amount'], oferta['shop']['name'], oferta['url'], validade, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                    ofertas_encontradas += 1
            
            conn_write.commit()
            conn_write.close()
            yield f"-> {ofertas_encontradas} ofertas encontradas e salvas no histórico."
            time.sleep(1.5)

        except Exception as e:
            yield f"ERRO ao buscar '{nome_jogo}': {e}"
    
    yield "\nAtualização concluída!"


def consultar_historico(id_jogo):
    """Consulta o histórico de preços para um jogo específico."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT data_consulta, nome_item, preco, loja, validade_oferta, link
        FROM historico_precos
        WHERE id_jogo_monitorado = ?
        ORDER BY data_consulta DESC, preco ASC
    """, (id_jogo,))
    historico = cursor.fetchall()
    # Formatando o preço para exibição
    historico_formatado = []
    for row in historico:
        # row é uma tupla, convertemos para lista para poder modificar
        row_list = list(row)
        # Formata a coluna de preço (índice 2)
        row_list[2] = f"R${row_list[2]:.2f}"
        historico_formatado.append(row_list)
    conn.close()
    return historico_formatado