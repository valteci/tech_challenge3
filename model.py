import pandas as pd
from utils import Season

class Preprocessing:

    DATA_PATH = './cleaned_data'

    def __init__(self):
        self._datas: list[pd.DataFrame] = []

    def _load_data(self) -> None:
        season = Season(19, 20)

        while season.next():
            file_name = f'{Preprocessing.DATA_PATH}/{season.date}.csv'
            df = pd.read_csv(file_name, sep=',')
            self._datas.append(df)


    @property
    def datas(self):
        """Getter method"""
        return self._datas
    

    @datas.setter
    def datas(self, value: list[pd.DataFrame]) -> None:
        """Setter method"""
        self._datas = value


    def add_total_goals(self, year_index: int = 0) -> None:
        """
        Para o DataFrame em self._datas[year_index], adiciona:
         - TotalHomeGoals: total de gols que o time mandante fez antes deste jogo
         - TotalAwayGoals: total de gols que o time visitante fez antes deste jogo
        """
        df = self._datas[year_index].copy()

        # 1) Monta visão “long” com event_id para garantir ordem cronológica
        df_home = df[['HomeTeam','FTHG']].rename(columns={'HomeTeam':'Team','FTHG':'Goals'}).copy()
        df_home['match_id'] = df.index
        df_home['side'] = 'home'
        df_home['event_id'] = df.index * 2

        df_away = df[['AwayTeam','FTAG']].rename(columns={'AwayTeam':'Team','FTAG':'Goals'}).copy()
        df_away['match_id'] = df.index
        df_away['side'] = 'away'
        df_away['event_id'] = df.index * 2 + 1

        df_long = pd.concat([df_home, df_away], ignore_index=True)
        df_long = df_long.sort_values('event_id')  # garante ordem: jogo0-home, jogo0-away, jogo1-home, ...

        # 2) Cálculo cumulativo por time, incluindo o evento atual, depois subtrai pra ficar só com anteriores
        df_long['CumSum'] = df_long.groupby('Team')['Goals'].cumsum()
        df_long['PrevGoals'] = df_long['CumSum'] - df_long['Goals']

        # 3) Pivot pra voltar a wide com match_id como índice
        pivot = df_long.pivot(index='match_id', columns='side', values='PrevGoals')

        # 4) Preenche (0 onde não existir) e atribui ao DataFrame original
        df['TotalHomeGoals']  = pivot['home'].fillna(0).astype(int).values
        df['TotalAwayGoals']  = pivot['away'].fillna(0).astype(int).values

        self._datas[year_index] = df




model = Preprocessing()
model._load_data()


print(model.datas[0].head())

print('\n========\n')

# Aplica o método ao primeiro ano
model.add_total_goals(0)

# Depois: têm as colunas TotalHomeGoals e TotalAwayGoals
print(model.datas[0])
model.datas[0].to_csv('teste.csv', sep=',', index=False)