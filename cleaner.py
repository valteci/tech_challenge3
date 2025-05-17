import pandas as pd
from utils import Season

base_dir = './data/england/premier_league'
saving_dir = './cleaned_data'
season = Season(19, 20)
CABECALHO = 'HomeTeam,AwayTeam,FTHG,FTAG,FTR'

def _clean_data(csv: str) -> str:
    rows = csv.split('\n')[1:]
    result = []

    for row in rows:
        if row == '':
            continue

        columns = row.split(',')
        
        home_team = columns[3]
        away_team = columns[4]
        home_goals = columns[5]
        away_goals = columns[6]
        resultado = columns[7]
        
        new_row = [
            home_team,
            away_team,
            home_goals,
            away_goals,
            resultado
        ]

        result.append(','.join(new_row))

    result.insert(0, CABECALHO)

    return '\n'.join(result)


def _save_data(datas: list[tuple[str, str]]) -> None:
    """
        datas: lista de tuplas: tuple(nome do arquivo, conteúdo)
    """
    FILE_CONTENT = 0
    FILE_NAME = 1

    for data in datas:
        file_name = f'{saving_dir}/{data[FILE_NAME]}.csv'
        with open(file_name, 'w') as file:
            file.write(data[FILE_CONTENT])


def clean_all() -> None:
    cleaned_data: list[tuple] = []

    while season.next():
        file_name = f'{base_dir}/{season.date}.csv'
        with open(file_name, 'r') as file:
            file_content = file.read()
            extracted_data = _clean_data(file_content)
            cleaned_data.append((extracted_data, season.date))
    
    _save_data(cleaned_data)


clean_all()
    



