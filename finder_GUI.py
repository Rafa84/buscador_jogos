# finder_GUI.py

import PySimpleGUI as sg
import backend # Importa nosso arquivo com toda a lógica
import json

# --- Inicialização ---
sg.theme('DarkTeal9') 
backend.setup_database() # Garante que o DB e as tabelas existam

# --- Funções de Apoio para a GUI ---
def atualizar_lista_jogos(window):
    """Lê os jogos do DB e atualiza o dropdown na janela."""
    jogos_no_db = backend.obter_jogos_monitorados()
    # O formato para o dropdown é uma lista de strings "Nome do Jogo"
    lista_formatada = [nome for id_jogo, nome in jogos_no_db]
    window['-LISTA_JOGOS-'].update(values=lista_formatada)
    return jogos_no_db

# --- Layout da Janela ---
layout_controle = [
    [sg.Text('Adicionar novo jogo para monitorar:')],
    [sg.Input(key='-NOME_JOGO-', size=(40,1)), sg.Button('Adicionar')],
    [sg.Button('ATUALIZAR PREÇOS DA INTERNET', size=(38, 2), button_color=('white', 'SeaGreen'))]
]

layout_consulta = [
    [sg.Text('Consultar histórico de um jogo:')],
    [sg.Combo([], key='-LISTA_JOGOS-', size=(38,1), enable_events=True, readonly=True)],
    [sg.Table(values=[], headings=['Data', 'Item', 'Preço', 'Loja', 'Validade', 'Link'],
              key='-TABELA_HISTORICO-',
              auto_size_columns=False,
              col_widths=[16, 30, 8, 12, 10, 30],
              justification='left',
              display_row_numbers=False,
              num_rows=15,
              expand_x=True,
              expand_y=True
              )]
]

layout = [
    [
        sg.Column(layout_controle, vertical_alignment='top'),
        sg.VSeparator(),
        sg.Column(layout_consulta)
    ],
    [sg.Text('Log de Atividades:')],
    [sg.Output(size=(120, 10), key='-STATUS-')]
]

# --- Criação da Janela ---
window = sg.Window('Finder v2.0 - Monitor de Preços de Jogos', layout, finalize=True)
jogos_mapeados = atualizar_lista_jogos(window) # Popula o dropdown e guarda o mapeamento nome -> id

# --- Loop de Eventos da Janela ---
while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break

    if event == 'Adicionar':
        nome_jogo = values['-NOME_JOGO-']
        resultado = backend.adicionar_novo_jogo(nome_jogo)
        print(f'-> {resultado}')
        window['-NOME_JOGO-'].update('') # Limpa o campo de texto
        jogos_mapeados = atualizar_lista_jogos(window)

    if event == 'ATUALIZAR PREÇOS DA INTERNET':
        try:
            with open('config.json', 'r') as f: config = json.load(f)
            API_KEY = config.get('API_KEY')
            if not API_KEY or "sua_chave" in API_KEY:
                print("!!! ERRO: Chave da API não configurada no 'config.json'.")
            else:
                window['ATUALIZAR PREÇOS DA INTERNET'].update(disabled=True)
                # O laço for vai imprimir o status em tempo real na janela
                for status_update in backend.buscar_e_salvar_precos(API_KEY, "BR"):
                    print(status_update)
                    window.refresh()
                window['ATUALIZAR PREÇOS DA INTERNET'].update(disabled=False)
        except Exception as e:
            print(f"!!! ERRO ao ler config.json ou ao atualizar preços: {e}")
            window['ATUALIZAR PREÇOS DA INTERNET'].update(disabled=False)


    if event == '-LISTA_JOGOS-':
        nome_selecionado = values['-LISTA_JOGOS-']
        if nome_selecionado:
            id_jogo_selecionado = [id_jogo for id_jogo, nome in jogos_mapeados if nome == nome_selecionado][0]
            historico = backend.consultar_historico(id_jogo_selecionado)
            window['-TABELA_HISTORICO-'].update(values=historico)

window.close()