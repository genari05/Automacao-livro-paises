import requests
import sqlite3
from bs4 import BeautifulSoup
import pandas as pd


class NomePaises:
    def __init__(self):
        self.paises = []

    def coletar(self):
        for pais in range(3):
            nome = input(f"Digite o nome do país {pais+1}: ")
            self.paises.append(nome.strip().lower())
        return self.paises


class ProcessadorPaises:
    def __init__(self, lista_paises):
        self.lista_paises = lista_paises
 
    def executar(self):
        for pais in self.lista_paises:
            try:
                url = f"https://restcountries.com/v3.1/name/{pais}"
                resposta = requests.get(url)
                dados = resposta.json()
                info = dados[0]

                nome = info['name']['common']
                oficial = info['name']['official']
                capital = info.get('capital', ['N/A'])[0]
                regiao = info.get('region', 'N/A')
                sub_regiao = info.get('subregion', 'N/A')
                populacao = str(info.get('population', '0'))
                area = str(info.get('area', '0.0'))
                idioma = ", ".join(info.get('languages', {}).values())
                fuso_horario = ", ".join(info.get('timezones', []))
                bandeira = info.get("flags", {}).get("png", "")

                moeda_info = info.get('currencies', {})
                moeda = "N/A"
                for codigo, dados_moeda in moeda_info.items():
                    moeda = f"{dados_moeda.get('name')} ({dados_moeda.get('symbol', '')})"
                    break

                print('\n=== Dados extraídos da API ===')
                print(f'Nome: {nome}')
                print(f'Nome oficial: {oficial}')
                print(f'Capital: {capital}')
                print(f'Região: {regiao}')
                print(f'Sub Região: {sub_regiao}')
                print(f'População: {populacao}')
                print(f'Área: {area}')
                print(f'Moeda: {moeda}')
                print(f'Idioma: {idioma}')
                print(f'Fuso horário: {fuso_horario}')
                print(f'Bandeira: {bandeira}')

                dados_pais = {
                    "nome": nome,
                    "oficial": oficial,
                    "capital": capital,
                    "regiao": regiao,
                    "sub_regiao": sub_regiao,
                    "populacao": populacao,
                    "area": area,
                    "moeda": moeda,
                    "idioma": idioma,
                    "fuso_horario": fuso_horario,
                    "bandeira": bandeira
                }

                self.salvar_no_banco(dados_pais)
                print('\nDados inseridos no banco com sucesso.\n')

            except Exception as e:
                print(f"Erro ao processar o país '{pais}': {e}")

    def salvar_no_banco(self, dados):
            with sqlite3.connect('paises.db') as conexao:
                cursor = conexao.cursor()

                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS paises (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT,
                        nome_oficial TEXT,
                        capital TEXT,
                        regiao TEXT,
                        sub_regiao TEXT,
                        populacao TEXT,
                        area TEXT,
                        moeda TEXT,
                        idioma TEXT,
                        fuso_horario TEXT,
                        bandeira TEXT
                    )
                ''')

                cursor.execute('''
                    INSERT INTO paises (
                        nome, nome_oficial, capital, regiao, sub_regiao,
                        populacao, area, moeda, idioma, fuso_horario, bandeira
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    dados["nome"], dados["oficial"], dados["capital"], dados["regiao"],
                    dados["sub_regiao"], dados["populacao"], dados["area"], dados["moeda"],
                    dados["idioma"], dados["fuso_horario"], dados["bandeira"]
                ))

                conexao.commit()


class ColetorLivros:
    def __init__(self):
        self.url_base = 'https://books.toscrape.com/'

    def coletar_livros(self, quantidade=10):
        url = self.url_base + 'index.html'
        resposta = requests.get(url)
        soup = BeautifulSoup(resposta.text, 'html.parser')

        livros_html = soup.find_all('article', class_='product_pod')
        livros_dados = []

        for livro in livros_html[:quantidade]:
            titulo = livro.h3.a['title']
            preco = livro.find('p', class_='price_color').text
            disponibilidade = livro.find('p', class_='instock availability').text.strip()

            
            classe_avaliacao = livro.find('p')['class']
            estrelas = classe_avaliacao[1] if len(classe_avaliacao) > 1 else 'Zero'

            livros_dados.append({
                'titulo': titulo,
                'preco': preco,
                'avaliacao': estrelas,
                'disponibilidade': disponibilidade
            })

        return livros_dados

    def salvar_no_banco(self, lista_livros):
        with sqlite3.connect('livraria.db') as conexao:
            cursor = conexao.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS livros (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT,
                    preco TEXT,
                    avaliacao TEXT,
                    disponibilidade TEXT
                )
            ''')

            for livro in lista_livros:
                cursor.execute('''
                    INSERT INTO livros (titulo, preco, avaliacao, disponibilidade)
                    VALUES (?, ?, ?, ?)
                ''', (
                    livro['titulo'],
                    livro['preco'],
                    livro['avaliacao'],
                    livro['disponibilidade']
                ))

            conexao.commit()
            print("Dados salvos com sucesso no banco de dados")

def gerar_relatorio():
    con_paises = sqlite3.connect('paises.db')
    con_livros = sqlite3.connect('livraria.db')

    dados_paises = pd.read_sql(f'SELECT * FROM paises', con_paises)
    dados_livros = pd.read_sql(f'SELECT * FROM livros', con_livros)

    with pd.ExcelWriter('relatorio.xlsx') as writer:
        dados_paises.to_excel(writer, sheet_name='Paises', index=False)
        dados_livros.to_excel(writer, sheet_name='Livros', index=False)

# === Execução principal ===
'''if __name__ == "__main__":
    coletor_paises = NomePaises()
    lista = coletor_paises.coletar()
    coletor_livro = ColetorLivros()
    livros = coletor_livro.coletar_livros(quantidade=10)
    coletor_livro.salvar_no_banco(livros)
    processador = ProcessadorPaises(lista)
    processador.executar()'''

gerar_relatorio()