import requests
import time
import json
from datetime import datetime, timedelta
import sqlite3

# --- CONFIGURAÇÃO ---
DB_FILE = "historico_de_precos.db"
HORAS_CACHE = 24 # Define que um resultado é considerado "recente" por até 24 horas
# --- FIM DA CONFIGURAÇÃO ---

def normalizar_nome_jogo(nome: str) -> str:
    """Limpa e padroniza o nome de um jogo para busca e cache."""
    nome_normalizado = nome.lower()
    # Substitui numerais romanos comuns
    substituicoes = {
        'iv': '4', 'iii': '3', 'ii': '2', 'v': '5', 'vi': '6', 
        'vii': '7', 'viii': '8', 'ix': '9', 'x': '10'
    }
    # Divide em palavras para substituir apenas o numeral isolado (ex: "iv" e não o "iv" em "drive")
    palavras = nome_normalizado.split()
    palavras_substituidas = []
    for p in palavras:
        palavras_substituidas.append(substituicoes.get(p, p))
    nome_normalizado = " ".join(palavras_substituidas)

    # Remove caracteres especiais
    caracteres_para_remover = "®™:-"
    for char in caracteres_para_remover:
        nome_normalizado = nome_normalizado.replace(char, "")
    
    # Remove espaços duplos que possam ter sido criados
    return " ".join(nome_normalizado.split())

def setup_database():
    """Cria o banco de dados e a tabela de histórico se não existirem."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historico_precos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            termo_busca TEXT NOT NULL,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            loja TEXT NOT NULL,
            link TEXT,
            validade_oferta TEXT,
            data_consulta TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def consultar_historico_recente(termo_busca_normalizado: str):
    """Verifica se existe um resultado recente para o termo de busca no banco de dados.
       Se sim, retorna TODOS os resultados daquela busca."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT MAX(data_consulta) FROM historico_precos WHERE termo_busca = ?", (termo_busca_normalizado,))
    resultado = cursor.fetchone()
    
    if resultado and resultado[0]:
        data_mais_recente_str = resultado[0]
        data_mais_recente = datetime.strptime(data_mais_recente_str, '%Y-%m-%d %H:%M:%S')
        
        if datetime.now() - data_mais_recente < timedelta(hours=HORAS_CACHE):
            print(f"\n-> Resultados para '{termo_busca_normalizado}' encontrados no histórico (de {data_mais_recente.strftime('%d/%m às %H:%M')}). Usando cache.")
            
            cursor.execute("SELECT nome, preco, loja, link, validade_oferta FROM historico_precos WHERE data_consulta = ?", (data_mais_recente_str,))
            
            resultados_do_cache = []
            for row in cursor.fetchall():
                nome, preco, loja, link, validade = row
                resultados_do_cache.append({
                    "nome": nome,
                    "preco_mais_baixo": f"R${preco:.2f}",
                    "loja": loja,
                    "validade_oferta": validade,
                    "link_da_oferta": link
                })
            conn.close()
            return resultados_do_cache
            
    conn.close()
    return None

def salvar_no_banco(termo_busca_normalizado, info_jogo):
    """Salva as informações de uma oferta, incluindo o termo que a originou."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO historico_precos (termo_busca, nome, preco, loja, link, validade_oferta, data_consulta) VALUES (?, ?, ?, ?, ?, ?, ?)', 
                   (termo_busca_normalizado, info_jogo['nome'], info_jogo['preco'], info_jogo['loja'], info_jogo['link_da_oferta'], info_jogo['validade_oferta'], datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()

def buscar_jogos_e_dlcs(API_KEY, nome_base_do_jogo: str) -> list:
    print(f"\nBuscando '{nome_base_do_jogo}' na internet...")
    try:
        url_busca = f"https://api.isthereanydeal.com/games/search/v1?key={API_KEY}&title={nome_base_do_jogo}&results=50"
        resposta_busca = requests.get(url_busca)
        resposta_busca.raise_for_status()
        dados_busca = resposta_busca.json()
        if not dados_busca:
            print(f"-> Nenhum item encontrado para '{nome_base_do_jogo}'.")
            return []
        print(f"-> Encontrados {len(dados_busca)} itens relacionados.")
        return dados_busca
    except requests.exceptions.RequestException as e:
        print(f"-> ERRO DE REDE na busca: {e}")
        return []

def obter_precos_para_lista_de_ids(API_KEY, PAIS, lista_de_ids: list) -> list:
    if not lista_de_ids: return []
    print(f"-> Obtendo preços para {len(lista_de_ids)} itens...")
    try:
        url_precos = f"https://api.isthereanydeal.com/games/prices/v3?key={API_KEY}&country={PAIS}"
        resposta_precos = requests.post(url_precos, json=lista_de_ids)
        resposta_precos.raise_for_status()
        return resposta_precos.json()
    except requests.exceptions.RequestException as e:
        print(f"-> ERRO DE REDE ao obter preços: {e}")
        return []

# --- BLOCO PRINCIPAL ---
if __name__ == "__main__":
    setup_database() 
    
    try:
        with open('config.json', 'r') as f: config = json.load(f)
        API_KEY = config.get('API_KEY')
    except Exception as e:
        print(f"ERRO ao carregar 'config.json': {e}")
        API_KEY = None

    if not API_KEY or "aqui_vai_a_sua_chave" in API_KEY:
        print("!!! ATENÇÃO: Configure sua chave da API no arquivo config.json.")
    else:
        entrada_usuario = input("Digite os nomes dos jogos que deseja buscar, separados por vírgula:\n> ")
        lista_de_jogos_base = [jogo.strip() for jogo in entrada_usuario.split(',')]
        resultados_finais = []

        for nome_jogo_original in lista_de_jogos_base:
            if not nome_jogo_original: continue
            
            nome_normalizado = normalizar_nome_jogo(nome_jogo_original)
            
            resultados_recentes = consultar_historico_recente(nome_normalizado)
            
            if resultados_recentes:
                resultados_finais.extend(resultados_recentes)
                continue
            
            jogos_encontrados = buscar_jogos_e_dlcs(API_KEY, nome_normalizado)
            if jogos_encontrados:
                ids_para_consultar = [jogo['id'] for jogo in jogos_encontrados]
                lista_de_precos = obter_precos_para_lista_de_ids(API_KEY, "BR", ids_para_consultar)
                precos_por_id = {item['id']: item for item in lista_de_precos}
                
                print(f" -> {len(jogos_encontrados)} itens processados. Salvando ofertas encontradas no histórico...")
                for jogo in jogos_encontrados:
                    id_jogo = jogo['id']
                    if id_jogo in precos_por_id and precos_por_id[id_jogo]['deals']:
                        oferta_mais_barata = min(precos_por_id[id_jogo]['deals'], key=lambda x: x['price']['amount'])
                        validade_str = "Sem data definida"
                        if oferta_mais_barata['expiry']:
                            data_obj = datetime.fromisoformat(oferta_mais_barata['expiry'])
                            validade_str = data_obj.strftime('%d/%m/%Y')
                        
                        info_oferta = { "nome": jogo['title'], "preco": oferta_mais_barata['price']['amount'], "preco_mais_baixo": f"R${oferta_mais_barata['price']['amount']:.2f}", "loja": oferta_mais_barata['shop']['name'], "validade_oferta": validade_str, "link_da_oferta": oferta_mais_barata['url'] }
                        resultados_finais.append(info_oferta)
                        salvar_no_banco(nome_normalizado, info_oferta)
            
            time.sleep(1.5)
        
        def obter_preco_para_ordenar(item):
            preco_str = item.get('preco_mais_baixo', 'R$0').replace('R$', '').replace(',', '.')
            return float(preco_str)

        resultados_ordenados = sorted(resultados_finais, key=obter_preco_para_ordenar)
        
        print("\n" + "="*50)
        print("RESULTADO DA CONSULTA (ORDENADO POR PREÇO)")
        print("="*50)
        
        if not resultados_ordenados:
            print("Nenhuma oferta foi encontrada para os jogos pesquisados.")
        else:
            for info in resultados_ordenados:
                print(f"Item: {info['nome']}")
                print(f"  -> Melhor Preço: {info['preco_mais_baixo']} na loja {info['loja']}")
                print(f"  -> Validade: {info['validade_oferta']}")
                print(f"  -> Link: {info['link_da_oferta']}")
                print("-" * 20)