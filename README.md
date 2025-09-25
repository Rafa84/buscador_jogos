# 🎮 Finder v2.0 - Monitor Inteligente de Preços de Jogos

![Python](https://img.shields.io/badge/Python-3.12-blue.svg)  
![License](https://img.shields.io/badge/License-MIT-green.svg)

Um aplicativo de desktop em **Python** para localizar promoções de jogos, DLCs e expansões, salvando o histórico de preços em um banco **SQLite** e exibindo tudo em uma interface simples com **PySimpleGUI**.

---

## ✨ Visão Geral

Com o Finder, você pode:  
- Adicionar jogos à sua lista de monitoramento.  
- Atualizar preços e promoções direto da API [IsThereAnyDeal](https://isthereanydeal.com/apps/api/).  
- Consultar o histórico de preços em uma tabela interativa.  

📸 **Capturas de Tela**  

![finder_gui](./assets/finder_gui.png) 
*(Exemplo da interface principal do Finder)*  

🎞️ **Demo em Ação**  

![finder_demo](./assets/finder_gui.gif)  
*(Exemplo de busca, atualização e consulta ao histórico)*  

---

## 📜 História do Projeto

A ideia surgiu quando precisei comprar DLCs do jogo **Northgard**.  
Enquanto algumas expansões estavam em promoção na **Nuuvem**, outras só apareciam na **Steam** — e os preços variavam bastante.  
Comparar manualmente foi frustrante, e então nasceu o **Finder**: um app para centralizar tudo em um só lugar.  

O projeto foi desenvolvido com auxílio das IAs **Gemini (Google)** e **ChatGPT (OpenAI)** como parceiras de brainstorming e depuração.  

---

## 🚀 Funcionalidades

- **Interface Gráfica** feita em PySimpleGUI.  
- **Busca Inteligente** de jogos + DLCs/expansões.  
- **Histórico Persistente** no SQLite.  
- **Cache Inteligente** para evitar chamadas desnecessárias à API.  
- **Normalização de Nomes** (ex.: entende que “Diablo IV” e “Diablo 4” são o mesmo jogo).  
- **Exportação** para `.csv` via `exportador.py`.  

---

## 🛠️ Tecnologias

- [Python 3.12+](https://www.python.org/)  
- [PySimpleGUI](https://pysimplegui.readthedocs.io/en/latest/)  
- [SQLite3](https://www.sqlite.org/)  
- [Requests](https://pypi.org/project/requests/)  
- [IsThereAnyDeal API](https://isthereanydeal.com/apps/api/)  

---

## ⚙️ Instalação e Configuração

1. **Clone este repositório**
   ```bash
   git clone https://github.com/SEU_USUARIO/buscador_jogos.git
   cd buscador_jogos
