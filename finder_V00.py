import requests
import time
import json # Importa a biblioteca para trabalhar com JSON
from datetime import datetime

# --- NOVO: CARREGANDO CONFIGURAÇÃO DO ARQUIVO JSON ---
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
        API_KEY = config.get('API_KEY')
except FileNotFoundError:
    print("ERRO: O arquivo 'config.json' não foi encontrado. Crie o arquivo com sua API Key.")
    API_KEY = None
except json.JSONDecodeError:
    print("ERRO: O arquivo 'config.json' está mal formatado.")
    API_KEY = None
# --- FIM DA NOVA SEÇÃO DE CONFIGURAÇÃO ---


PAIS = "BR"


def buscar_jogos_e_dlcs(nome_base_do_jogo: str) -> list:
    print(f"\nBuscando por '{nome_base_do_jogo}' e seus conteúdos...")
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

def obter_precos_para_lista_de_ids(lista_de_ids: list) -> list:
    if not lista_de_ids:
        return []
        
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
    if not API_KEY or "aqui_vai_a_sua_chave" in API_KEY:
        print("!!! ATENÇÃO: Você precisa configurar sua chave da API no arquivo config.json antes de rodar.")
    else:
        entrada_usuario = input("Digite os nomes dos jogos que deseja buscar, separados por vírgula:\n> ")
        lista_de_jogos_base = [jogo.strip() for jogo in entrada_usuario.split(',')]

        resultados_finais = []
        
        for nome_jogo in lista_de_jogos_base:
            if not nome_jogo:
                continue
            
            jogos_encontrados = buscar_jogos_e_dlcs(nome_jogo)
            
            if jogos_encontrados:
                ids_para_consultar = [jogo['id'] for jogo in jogos_encontrados]
                lista_de_precos = obter_precos_para_lista_de_ids(ids_para_consultar)
                
                precos_por_id = {item['id']: item for item in lista_de_precos}
                
                for jogo in jogos_encontrados:
                    id_jogo = jogo['id']
                    if id_jogo in precos_por_id and precos_por_id[id_jogo]['deals']:
                        lista_de_ofertas = precos_por_id[id_jogo]['deals']
                        oferta_mais_barata = min(lista_de_ofertas, key=lambda x: x['price']['amount'])
                        
                        validade_str = "Sem data definida"
                        if oferta_mais_barata['expiry']:
                            data_obj = datetime.fromisoformat(oferta_mais_barata['expiry'])
                            validade_str = data_obj.strftime('%d/%m/%Y')
                            
                        resultados_finais.append({
                            "nome": jogo['title'],
                            "preco": oferta_mais_barata['price']['amount'],
                            "preco_mais_baixo": f"R${oferta_mais_barata['price']['amount']:.2f}",
                            "loja": oferta_mais_barata['shop']['name'],
                            "validade_oferta": validade_str,
                            "link_da_oferta": oferta_mais_barata['url']
                        })
            
            time.sleep(1)
        
        resultados_ordenados = sorted(resultados_finais, key=lambda x: x['preco'])
        
        print("\n" + "="*50)
        print("RESULTADO FINAL DA BUSCA DE PREÇOS")
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