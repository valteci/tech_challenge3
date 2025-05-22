import requests
from time import sleep
from pathlib import Path
import os

from utils import (
    Season,
    BASE_URL_ELITE,
    ENGLAND_LEAGUES,
    GERMANY_LEAGUES,
    SPAIN_LEAGUES,
    ITALY_LEAGUES,
    FRANCE_LEAGUES,
    SCOTLAND_LEAGUES,
    NETHERLANDS_LEAGUES,
    BELGIUM_LEAGUES,
    PORTUGAL_LEAGUES,
    TURKEY_LEAGUES,
    GREECE_LEAGUES,
    ARGENTINA_LEAGUE,
    AUSTRIA_LEAGUE,
    BRASIL_LEAGUE,
    CHINA_LEAGUES,
    DINAMARCA_LEAGUES,
    FINLANDIA_LEAGUES,
    IRLANDA_LEAGUES,
    JAPAO_LEAGUES,
    MEXICO_LEAGUES,
    NORUEGA_LEAGUES,
    POLONIA_LEAGUES,
    ROMENIA_LEAGUES,
    RUSSIA_LEAGUES,
    SUECIA_LEAGUES,
    SUICIA_LEAGUES,
    EUA_LEAGUES,
    BASE_URL,
    HEADERS,
    ESTRUTURA_DIR
)


class Downloader:
    def __init__(self):
        self._criar_estrutura_diretorios()

    def atualizar(self):
        pass

    def baixar_todos(self):
        self._baixar_england()
        self._baixar_germany()
        self._baixar_spain()
        self._baixar_italia()
        self._baixar_franca()
        self._baixar_scotland()
        self._baixar_netherlands()
        self._baixar_belgium()
        self._baixar_portugal()
        self._baixar_turkey()
        self._baixar_greece()
        self._baixar_argentina()
        self._baixar_austria()
        self._baixar_brasil()
        self._baixar_china()
        self._baixar_dinamarca()
        self._baixar_finlandia()
        self._baixar_irlanda()
        self._baixar_japao()
        self._baixar_mexico()
        self._baixar_noruega()
        self._baixar_polonia()
        self._baixar_romenia()
        self._baixar_russia()
        self._baixar_suecia()
        self._baixar_suicia()
        self._baixar_eua()

    
    def _criar_estrutura_diretorios(
            self,
            base_dir: str = './data'
    ) -> None:
        
        
        
        base_path = Path(base_dir)
        

        base_path.mkdir(parents=True, exist_ok=True)

        for pais, competicoes in ESTRUTURA_DIR.items():
            pais_path = base_path / pais
            pais_path.mkdir(exist_ok=True)

            for competicao in competicoes:
                comp_path = pais_path / competicao
                comp_path.mkdir(exist_ok=True)



    def _baixar_england(self) -> None:
        save_path = {
            ENGLAND_LEAGUES[0]: './data/england/premier_league',
            ENGLAND_LEAGUES[1]: './data/england/Championship',
            ENGLAND_LEAGUES[2]: './data/england/League_1',
            ENGLAND_LEAGUES[3]: './data/england/League_2',
        }

        for liga in ENGLAND_LEAGUES:
            season = Season(92, 93)
            while season.next():
                try:
                    url = f'{BASE_URL_ELITE}/{season.date}/{liga}.csv'
                    response = requests.get(url=url, headers=HEADERS)
                    response.raise_for_status()
                    path = save_path[liga]
                    filename = f'{path}/{season.date}.csv'
                    with open(filename, 'w') as file:
                        csv = response.text
                        file.write(csv)
                    
                    print(f'CSV da {liga} ano {season.date} baixado com sucesso!')
                    sleep(2)

                except Exception as e:
                    print(f'Erro ao tentar baixar liga: {liga} ano {season.date} erro: ', e)
            
            print('=' * 15)


    def _baixar_germany(self) -> None:
        save_path = {
            GERMANY_LEAGUES[0]: './data/germany/Bundesliga_1',
            GERMANY_LEAGUES[1]: './data/germany/Bundesliga_2',
        }

        for liga in GERMANY_LEAGUES:
            season = Season(92, 93)
            while season.next():
                try:
                    url = f'{BASE_URL_ELITE}/{season.date}/{liga}.csv'
                    response = requests.get(url=url, headers=HEADERS)
                    response.raise_for_status()
                    path = save_path[liga]
                    filename = f'{path}/{season.date}.csv'
                    with open(filename, 'w') as file:
                        csv = response.text
                        file.write(csv)
                    
                    print(f'CSV da {liga} ano {season.date} baixado com sucesso!')
                    sleep(2)

                except Exception as e:
                    print(f'Erro ao tentar baixar liga: {liga} ano {season.date} erro: ', e)
            
            print('=' * 15)


    def _baixar_spain(self) -> None:
        save_path = {
            SPAIN_LEAGUES[0]: './data/spain/La_liga_primeira_d',
            SPAIN_LEAGUES[1]: './data/spain/La_liga_segunda_d',
        }

        # anos faltantes ds SP2
        excludeds = ['9394', '9495', '9596']

        for liga in SPAIN_LEAGUES:
            season = Season(92, 93)
            while season.next():
                if (liga == 'SP2') and season.date in excludeds:
                    continue

                try:
                    url = f'{BASE_URL_ELITE}/{season.date}/{liga}.csv'
                    response = requests.get(url=url, headers=HEADERS)
                    response.raise_for_status()
                    path = save_path[liga]
                    filename = f'{path}/{season.date}.csv'
                    with open(filename, 'w') as file:
                        csv = response.text
                        file.write(csv)
                    
                    print(f'CSV da {liga} ano {season.date} baixado com sucesso!')
                    sleep(2)

                except Exception as e:
                    print(f'Erro ao tentar baixar liga: {liga} ano {season.date} erro: ', e)
            
            print('=' * 15)


    def _baixar_italia(self) -> None:
        save_path = {
            ITALY_LEAGUES[0]: './data/italy/Serie_A',
            ITALY_LEAGUES[1]: './data/italy/Serie_B',
        }

        # anos faltantes ds I2
        excludeds = ['9394', '9495', '9596', '9697']

        for liga in ITALY_LEAGUES:
            season = Season(92, 93)
            while season.next():
                if (liga == 'I2') and season.date in excludeds:
                    continue

                try:
                    url = f'{BASE_URL_ELITE}/{season.date}/{liga}.csv'
                    response = requests.get(url=url, headers=HEADERS)
                    response.raise_for_status()
                    path = save_path[liga]
                    filename = f'{path}/{season.date}.csv'
                    with open(filename, 'w') as file:
                        csv = response.text
                        file.write(csv)
                    
                    print(f'CSV da {liga} ano {season.date} baixado com sucesso!')
                    sleep(2)

                except Exception as e:
                    print(f'Erro ao tentar baixar liga: {liga} ano {season.date} erro: ', e)
            
            print('=' * 15)


    def _baixar_franca(self) -> None:
        save_path = {
            FRANCE_LEAGUES[0]: './data/france/Ligue_1',
            FRANCE_LEAGUES[1]: './data/france/Ligue_2',
        }

        # anos faltantes ds F2
        excludeds = ['9394', '9495', '9596']

        for liga in FRANCE_LEAGUES:
            season = Season(92, 93)
            while season.next():
                if (liga == 'F2') and season.date in excludeds:
                    continue

                try:
                    url = f'{BASE_URL_ELITE}/{season.date}/{liga}.csv'
                    response = requests.get(url=url, headers=HEADERS)
                    response.raise_for_status()
                    path = save_path[liga]
                    filename = f'{path}/{season.date}.csv'
                    with open(filename, 'w') as file:
                        csv = response.text
                        file.write(csv)
                    
                    print(f'CSV da {liga} ano {season.date} baixado com sucesso!')
                    sleep(2)

                except Exception as e:
                    print(f'Erro ao tentar baixar liga: {liga} ano {season.date} erro: ', e)
            
            print('=' * 15)


    def _baixar_scotland(self) -> None:
        save_path = {
            SCOTLAND_LEAGUES[0]: './data/scotland/Premier_league',
            SCOTLAND_LEAGUES[1]: './data/scotland/D1',
            SCOTLAND_LEAGUES[2]: './data/scotland/D2',
            SCOTLAND_LEAGUES[3]: './data/scotland/D3'
        }

        # anos faltantes ds F2
        excludeds = [
            ('SC2', '9495'),
            ('SC2', '9596'),
            ('SC2', '9697'),
            ('SC3', '9495'),
            ('SC3', '9596'),
            ('SC3', '9697'),
        ]

        for liga in SCOTLAND_LEAGUES:
            season = Season(93, 94)
            while season.next():
                if (liga, season.date) in excludeds:
                    continue

                try:
                    url = f'{BASE_URL_ELITE}/{season.date}/{liga}.csv'
                    response = requests.get(url=url, headers=HEADERS)
                    response.raise_for_status()
                    path = save_path[liga]
                    filename = f'{path}/{season.date}.csv'
                    with open(filename, 'w') as file:
                        csv = response.text
                        file.write(csv)
                    
                    print(f'CSV da {liga} ano {season.date} baixado com sucesso!')
                    sleep(2)

                except Exception as e:
                    print(f'Erro ao tentar baixar liga: {liga} ano {season.date} erro: ', e)
            
            print('=' * 15)


    def _baixar_netherlands(self) -> None:
        save_path = {
            NETHERLANDS_LEAGUES[0]: './data/netherlands/Eredivisie',
        }

        for liga in NETHERLANDS_LEAGUES:
            season = Season(92, 93)
            while season.next():
                try:
                    url = f'{BASE_URL_ELITE}/{season.date}/{liga}.csv'
                    response = requests.get(url=url, headers=HEADERS)
                    response.raise_for_status()
                    path = save_path[liga]
                    filename = f'{path}/{season.date}.csv'
                    with open(filename, 'w') as file:
                        csv = response.text
                        file.write(csv)
                    
                    print(f'CSV da {liga} ano {season.date} baixado com sucesso!')
                    sleep(2)

                except Exception as e:
                    print(f'Erro ao tentar baixar liga: {liga} ano {season.date} erro: ', e)
            
            print('=' * 15)


    def _baixar_belgium(self) -> None:
        save_path = {
            BELGIUM_LEAGUES[0]: './data/belgium/Jupiler',
        }

        for liga in BELGIUM_LEAGUES:
            season = Season(94, 95)
            while season.next():
                try:
                    url = f'{BASE_URL_ELITE}/{season.date}/{liga}.csv'
                    response = requests.get(url=url, headers=HEADERS)
                    response.raise_for_status()
                    path = save_path[liga]
                    filename = f'{path}/{season.date}.csv'
                    with open(filename, 'w') as file:
                        csv = response.text
                        file.write(csv)
                    
                    print(f'CSV da {liga} ano {season.date} baixado com sucesso!')
                    sleep(2)

                except Exception as e:
                    print(f'Erro ao tentar baixar liga: {liga} ano {season.date} erro: ', e)
            
            print('=' * 15)


    def _baixar_portugal(self) -> None:
        save_path = {
            PORTUGAL_LEAGUES[0]: './data/portugal/Primeira_liga',
        }

        for liga in PORTUGAL_LEAGUES:
            season = Season(93, 94)
            while season.next():
                try:
                    url = f'{BASE_URL_ELITE}/{season.date}/{liga}.csv'
                    response = requests.get(url=url, headers=HEADERS)
                    response.raise_for_status()
                    path = save_path[liga]
                    filename = f'{path}/{season.date}.csv'
                    with open(filename, 'w') as file:
                        csv = response.text
                        file.write(csv)
                    
                    print(f'CSV da {liga} ano {season.date} baixado com sucesso!')
                    sleep(2)

                except Exception as e:
                    print(f'Erro ao tentar baixar liga: {liga} ano {season.date} erro: ', e)
            
            print('=' * 15)


    def _baixar_turkey(self) -> None:
        save_path = {
            TURKEY_LEAGUES[0]: './data/turkey/TFF_ligi_1',
        }

        for liga in TURKEY_LEAGUES:
            season = Season(93, 94)
            while season.next():
                try:
                    url = f'{BASE_URL_ELITE}/{season.date}/{liga}.csv'
                    response = requests.get(url=url, headers=HEADERS)
                    response.raise_for_status()
                    path = save_path[liga]
                    filename = f'{path}/{season.date}.csv'
                    with open(filename, 'w') as file:
                        csv = response.text
                        file.write(csv)
                    
                    print(f'CSV da {liga} ano {season.date} baixado com sucesso!')
                    sleep(2)

                except Exception as e:
                    print(f'Erro ao tentar baixar liga: {liga} ano {season.date} erro: ', e)
            
            print('=' * 15)


    def _baixar_greece(self) -> None:
        save_path = {
            GREECE_LEAGUES[0]: './data/greece/Ethniki_katigoria',
        }

        for liga in GREECE_LEAGUES:
            season = Season(93, 94)
            while season.next():
                try:
                    url = f'{BASE_URL_ELITE}/{season.date}/{liga}.csv'
                    response = requests.get(url=url, headers=HEADERS)
                    response.raise_for_status()
                    path = save_path[liga]
                    filename = f'{path}/{season.date}.csv'
                    with open(filename, 'w') as file:
                        csv = response.text
                        file.write(csv)
                    
                    print(f'CSV da {liga} ano {season.date} baixado com sucesso!')
                    sleep(2)

                except Exception as e:
                    print(f'Erro ao tentar baixar liga: {liga} ano {season.date} erro: ', e)
            
            print('=' * 15)


    def _baixar_argentina(self) -> None:
        save_path = './data/argentina/Campeonato'
        url = f'{BASE_URL}/{ARGENTINA_LEAGUE}.csv'

        try:
            response = requests.get(url=url, headers=HEADERS)
            response.raise_for_status()
            file_name = f'{save_path}/argentina.csv'
            with open(file_name, 'w') as file:
                csv = response.text
                file.write(csv)

            print(f'CSV da {ARGENTINA_LEAGUE} baixado com sucesso!')
            sleep(2)
            

        except Exception as e:
            print(f'Erro ao tentar baixar liga: {ARGENTINA_LEAGUE}, erro: ', e)


    def _baixar_austria(self) -> None:
        save_path = './data/austria/Campeonato'
        url = f'{BASE_URL}/{AUSTRIA_LEAGUE}.csv'

        try:
            response = requests.get(url=url, headers=HEADERS)
            response.raise_for_status()
            file_name = f'{save_path}/austria.csv'
            with open(file_name, 'w') as file:
                csv = response.text
                file.write(csv)

            print(f'CSV da {AUSTRIA_LEAGUE} baixado com sucesso!')
            sleep(2)
            

        except Exception as e:
            print(f'Erro ao tentar baixar liga: {AUSTRIA_LEAGUE}, erro: ', e)


    def _baixar_brasil(self) -> None:
        save_path = './data/brasil/Campeonato'
        url = f'{BASE_URL}/{BRASIL_LEAGUE}.csv'

        try:
            response = requests.get(url=url, headers=HEADERS)
            response.raise_for_status()
            file_name = f'{save_path}/brasil.csv'
            with open(file_name, 'w') as file:
                csv = response.text
                file.write(csv)

            print(f'CSV da {BRASIL_LEAGUE} baixado com sucesso!')
            sleep(2)
            

        except Exception as e:
            print(f'Erro ao tentar baixar liga: {BRASIL_LEAGUE}, erro: ', e)


    def _baixar_china(self) -> None:
        save_path = './data/china/Campeonato'
        url = f'{BASE_URL}/{CHINA_LEAGUES}.csv'

        try:
            response = requests.get(url=url, headers=HEADERS)
            response.raise_for_status()
            file_name = f'{save_path}/china.csv'
            with open(file_name, 'w') as file:
                csv = response.text
                file.write(csv)

            print(f'CSV da {CHINA_LEAGUES} baixado com sucesso!')
            sleep(2)
            

        except Exception as e:
            print(f'Erro ao tentar baixar liga: {CHINA_LEAGUES}, erro: ', e)


    def _baixar_dinamarca(self) -> None:
        save_path = './data/dinamarca/Campeonato'
        url = f'{BASE_URL}/{DINAMARCA_LEAGUES}.csv'

        try:
            response = requests.get(url=url, headers=HEADERS)
            response.raise_for_status()
            file_name = f'{save_path}/dinamarca.csv'
            with open(file_name, 'w') as file:
                csv = response.text
                file.write(csv)

            print(f'CSV da {DINAMARCA_LEAGUES} baixado com sucesso!')
            sleep(2)
            

        except Exception as e:
            print(f'Erro ao tentar baixar liga: {DINAMARCA_LEAGUES}, erro: ', e)


    def _baixar_finlandia(self) -> None:
        save_path = './data/finlandia/Campeonato'
        url = f'{BASE_URL}/{FINLANDIA_LEAGUES}.csv'

        try:
            response = requests.get(url=url, headers=HEADERS)
            response.raise_for_status()
            file_name = f'{save_path}/finlandia.csv'
            with open(file_name, 'w') as file:
                csv = response.text
                file.write(csv)

            print(f'CSV da {FINLANDIA_LEAGUES} baixado com sucesso!')
            sleep(2)
            

        except Exception as e:
            print(f'Erro ao tentar baixar liga: {FINLANDIA_LEAGUES}, erro: ', e)


    def _baixar_irlanda(self) -> None:
        save_path = './data/irlanda/Campeonato'
        url = f'{BASE_URL}/{IRLANDA_LEAGUES}.csv'

        try:
            response = requests.get(url=url, headers=HEADERS)
            response.raise_for_status()
            file_name = f'{save_path}/irlanda.csv'
            with open(file_name, 'w') as file:
                csv = response.text
                file.write(csv)

            print(f'CSV da {IRLANDA_LEAGUES} baixado com sucesso!')
            sleep(2)
            

        except Exception as e:
            print(f'Erro ao tentar baixar liga: {IRLANDA_LEAGUES}, erro: ', e)


    def _baixar_japao(self) -> None:
        save_path = './data/japao/Campeonato'
        url = f'{BASE_URL}/{JAPAO_LEAGUES}.csv'

        try:
            response = requests.get(url=url, headers=HEADERS)
            response.raise_for_status()
            file_name = f'{save_path}/japao.csv'
            with open(file_name, 'w') as file:
                csv = response.text
                file.write(csv)

            print(f'CSV da {JAPAO_LEAGUES} baixado com sucesso!')
            sleep(2)
            

        except Exception as e:
            print(f'Erro ao tentar baixar liga: {JAPAO_LEAGUES}, erro: ', e)


    def _baixar_mexico(self) -> None:
        save_path = './data/mexico/Campeonato'
        url = f'{BASE_URL}/{MEXICO_LEAGUES}.csv'

        try:
            response = requests.get(url=url, headers=HEADERS)
            response.raise_for_status()
            file_name = f'{save_path}/mexico.csv'
            with open(file_name, 'w') as file:
                csv = response.text
                file.write(csv)

            print(f'CSV da {MEXICO_LEAGUES} baixado com sucesso!')
            sleep(2)
            

        except Exception as e:
            print(f'Erro ao tentar baixar liga: {MEXICO_LEAGUES}, erro: ', e)


    def _baixar_noruega(self) -> None:
        save_path = './data/noruega/Campeonato'
        url = f'{BASE_URL}/{NORUEGA_LEAGUES}.csv'

        try:
            response = requests.get(url=url, headers=HEADERS)
            response.raise_for_status()
            file_name = f'{save_path}/noruega.csv'
            with open(file_name, 'w') as file:
                csv = response.text
                file.write(csv)

            print(f'CSV da {NORUEGA_LEAGUES} baixado com sucesso!')
            sleep(2)
            

        except Exception as e:
            print(f'Erro ao tentar baixar liga: {NORUEGA_LEAGUES}, erro: ', e)


    def _baixar_polonia(self) -> None:
        save_path = './data/polonia/Campeonato'
        url = f'{BASE_URL}/{POLONIA_LEAGUES}.csv'

        try:
            response = requests.get(url=url, headers=HEADERS)
            response.raise_for_status()
            file_name = f'{save_path}/polonia.csv'
            with open(file_name, 'w') as file:
                csv = response.text
                file.write(csv)

            print(f'CSV da {POLONIA_LEAGUES} baixado com sucesso!')
            sleep(2)
            

        except Exception as e:
            print(f'Erro ao tentar baixar liga: {POLONIA_LEAGUES}, erro: ', e)


    def _baixar_romenia(self) -> None:
        save_path = './data/romenia/Campeonato'
        url = f'{BASE_URL}/{ROMENIA_LEAGUES}.csv'

        try:
            response = requests.get(url=url, headers=HEADERS)
            response.raise_for_status()
            file_name = f'{save_path}/romenia.csv'
            with open(file_name, 'w') as file:
                csv = response.text
                file.write(csv)

            print(f'CSV da {ROMENIA_LEAGUES} baixado com sucesso!')
            sleep(2)
            

        except Exception as e:
            print(f'Erro ao tentar baixar liga: {ROMENIA_LEAGUES}, erro: ', e)


    def _baixar_russia(self) -> None:
        save_path = './data/russia/Campeonato'
        url = f'{BASE_URL}/{RUSSIA_LEAGUES}.csv'

        try:
            response = requests.get(url=url, headers=HEADERS)
            response.raise_for_status()
            file_name = f'{save_path}/russia.csv'
            with open(file_name, 'w') as file:
                csv = response.text
                file.write(csv)

            print(f'CSV da {RUSSIA_LEAGUES} baixado com sucesso!')
            sleep(2)
            

        except Exception as e:
            print(f'Erro ao tentar baixar liga: {RUSSIA_LEAGUES}, erro: ', e)


    def _baixar_suecia(self) -> None:
        save_path = './data/suecia/Campeonato'
        url = f'{BASE_URL}/{SUECIA_LEAGUES}.csv'

        try:
            response = requests.get(url=url, headers=HEADERS)
            response.raise_for_status()
            file_name = f'{save_path}/suecia.csv'
            with open(file_name, 'w') as file:
                csv = response.text
                file.write(csv)

            print(f'CSV da {SUECIA_LEAGUES} baixado com sucesso!')
            sleep(2)
            

        except Exception as e:
            print(f'Erro ao tentar baixar liga: {SUECIA_LEAGUES}, erro: ', e)


    def _baixar_suicia(self) -> None:
        save_path = './data/suicia/Campeonato'
        url = f'{BASE_URL}/{SUICIA_LEAGUES}.csv'

        try:
            response = requests.get(url=url, headers=HEADERS)
            response.raise_for_status()
            file_name = f'{save_path}/suicia.csv'
            with open(file_name, 'w') as file:
                csv = response.text
                file.write(csv)

            print(f'CSV da {SUICIA_LEAGUES} baixado com sucesso!')
            sleep(2)
            

        except Exception as e:
            print(f'Erro ao tentar baixar liga: {SUICIA_LEAGUES}, erro: ', e)


    def _baixar_eua(self) -> None:
        save_path = './data/eua/Campeonato'
        url = f'{BASE_URL}/{EUA_LEAGUES}.csv'

        try:
            response = requests.get(url=url, headers=HEADERS)
            response.raise_for_status()
            file_name = f'{save_path}/eua.csv'
            with open(file_name, 'w') as file:
                csv = response.text
                file.write(csv)

            print(f'CSV da {EUA_LEAGUES} baixado com sucesso!')
            sleep(2)
            

        except Exception as e:
            print(f'Erro ao tentar baixar liga: {EUA_LEAGUES}, erro: ', e)


a = Downloader()
a._baixar_england()