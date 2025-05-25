import pandas as pd
from MLpipeline.utils import Season

base_dir = './data/england/premier_league' # diretório onde vai ser pego os dados
saving_dir = './cleaned_data' # diretórios onde vão ser salvos os dados
season = Season(92, 93) # limite inferior
CABECALHO = 'HomeTeam,AwayTeam,FTHG,FTAG,FTR' # cabeçalho do csv.

def _clean_data(csv: str) -> str:
    header = csv.split('\n')[0]
    header_columns = header.split(',')
    has_time_column = 'Time' in header_columns

    rows = csv.split('\n')[1:]
    result = []

    for row in rows:
        if row == '':
            continue

        columns = row.split(',')
        
        if has_time_column:
            home_team = columns[3]
            away_team = columns[4]
            home_goals = columns[5]
            away_goals = columns[6]
            resultado = columns[7]
        else:
            home_team = columns[2]
            away_team = columns[3]
            home_goals = columns[4]
            away_goals = columns[5]
            resultado = columns[6]
        
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


    



