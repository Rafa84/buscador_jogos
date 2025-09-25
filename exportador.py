import sqlite3
import csv

# --- CONFIGURAÇÃO ---
DB_FILE = "historico_de_precos.db"
CSV_FILE = "historico_precos.csv"
# --- FIM DA CONFIGURAÇÃO ---

def exportar_para_csv():
    """
    Lê os dados do banco SQLite e os exporta para um arquivo CSV.
    """
    try:
        # 1. Conecta ao banco de dados
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # 2. Executa a consulta para pegar todos os dados do histórico
        print(f"Lendo dados do banco de dados '{DB_FILE}'...")
        cursor.execute("SELECT * FROM historico_precos")
        
        # 3. Pega os nomes das colunas (cabeçalho)
        headers = [description[0] for description in cursor.description]
        
        # 4. Pega todas as linhas de dados
        rows = cursor.fetchall()

        if not rows:
            print("O banco de dados de histórico está vazio. Nada para exportar.")
            return

        # 5. Escreve os dados no arquivo CSV
        print(f"Escrevendo {len(rows)} registros no arquivo '{CSV_FILE}'...")
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Escreve o cabeçalho
            writer.writerow(headers)
            
            # Escreve todas as linhas de dados
            writer.writerows(rows)
        
        print(f"\n✅ Exportação concluída com sucesso! O arquivo '{CSV_FILE}' foi criado.")

    except sqlite3.OperationalError as e:
        print(f"ERRO: Ocorreu um erro ao acessar o banco de dados. Ele existe? Detalhes: {e}")
    except Exception as e:
        print(f"ERRO: Ocorreu um erro inesperado: {e}")
    finally:
        # Garante que a conexão com o banco seja fechada
        if 'conn' in locals() and conn:
            conn.close()

# --- BLOCO PRINCIPAL ---
if __name__ == "__main__":
    exportar_para_csv()