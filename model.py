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


    def add_gols_conceded(self, year_index: int = 0) -> None:
        """
        Para o DataFrame em self._datas[year_index], adiciona:
         - TotalHomeConceded: gols sofridos pelo mandante em jogos anteriores
         - TotalAwayConceded: gols sofridos pelo visitante em jogos anteriores
        """
        df = self._datas[year_index].copy()

        # 1) Cria visão "long" com gols sofridos
        df_home = (
            df[['HomeTeam','FTAG']]
            .rename(columns={'HomeTeam':'Team','FTAG':'Goals'})
            .assign(match_id=df.index, side='home', event_id=df.index*2)
        )
        df_away = (
            df[['AwayTeam','FTHG']]
            .rename(columns={'AwayTeam':'Team','FTHG':'Goals'})
            .assign(match_id=df.index, side='away', event_id=df.index*2+1)
        )

        df_long = pd.concat([df_home, df_away], ignore_index=True)
        df_long = df_long.sort_values('event_id')

        # 2) Cumsum incluindo o atual e subtrai para ficar só com anteriores
        df_long['CumSum'] = df_long.groupby('Team')['Goals'].cumsum()
        df_long['PrevConceded'] = df_long['CumSum'] - df_long['Goals']

        # 3) Pivot de volta para wide
        pivot = df_long.pivot(index='match_id', columns='side', values='PrevConceded')

        # 4) Atribui e atualiza
        df['TotalHomeConceded'] = pivot['home'].fillna(0).astype(int).values
        df['TotalAwayConceded'] = pivot['away'].fillna(0).astype(int).values

        self._datas[year_index] = df


    def add_total_matches(self, year_index: int = 0) -> None:
        """
        Para o DataFrame em self._datas[year_index], adiciona:
         - TotalHomeMatches: quantidade de partidas já jogadas pelo mandante antes deste jogo
         - TotalAwayMatches: quantidade de partidas já jogadas pelo visitante antes deste jogo
        """
        df = self._datas[year_index].copy()

        # 1) Cria visão “long” com um registro por participação de time
        df_home = (
            df[['HomeTeam']]
            .rename(columns={'HomeTeam':'Team'})
            .assign(Count=1,
                    match_id=df.index,
                    side='home',
                    event_id=df.index * 2)
        )
        df_away = (
            df[['AwayTeam']]
            .rename(columns={'AwayTeam':'Team'})
            .assign(Count=1,
                    match_id=df.index,
                    side='away',
                    event_id=df.index * 2 + 1)
        )

        df_long = pd.concat([df_home, df_away], ignore_index=True)
        # Ordena eventos para respeitar ordem cronológica por partida e por side
        df_long = df_long.sort_values('event_id')

        # 2) Soma cumulativa de participações (jogos), incluindo o atual, e subtrai 1 para ficar só com anteriores
        df_long['CumMatches'] = df_long.groupby('Team')['Count'].cumsum()
        df_long['PrevMatches'] = df_long['CumMatches'] - df_long['Count']

        # 3) Pivot de volta para wide
        pivot = df_long.pivot(index='match_id', columns='side', values='PrevMatches')

        # 4) Atribui ao DataFrame original e atualiza
        df['TotalHomeMatches'] = pivot['home'].fillna(0).astype(int).values
        df['TotalAwayMatches'] = pivot['away'].fillna(0).astype(int).values

        self._datas[year_index] = df
    




model = Preprocessing()
model._load_data()


print(model.datas[0].head())

print('\n========\n')

# Aplica o método ao primeiro ano
model.datas[0].iloc[:, [2, 3]] = 1
model.add_total_matches(0)
model.add_total_goals(0)
model.add_gols_conceded(0)


# Depois: têm as colunas TotalHomeGoals e TotalAwayGoals
print(model.datas[0])
model.datas[0].to_csv('teste.csv', sep=',', index=False)