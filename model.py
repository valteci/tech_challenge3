import pandas as pd
import numpy as np
from utils import Season

class Preprocessing:

    DATA_PATH = './cleaned_data'

    def __init__(self):
        self._datas: list[pd.DataFrame] = []

        self._features = {
            self.add_goals_scored: False,
            self.add_goals_conceded: False,
            self.add_total_matches: False,
            self.add_total_points: False,
            self.add_average_gols_scored: False,
            self.add_average_gols_conceded: False,
            self.add_ppg: False,
            self.add_last_n_average_gols_scored: False
        }

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

    # Métricas base
    def add_goals_scored(self, year_index: int = 0) -> None:
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
        self._features[self.add_goals_scored] = True


    def add_goals_conceded(self, year_index: int = 0) -> None:
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
        self._features[self.add_goals_conceded] = True


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
        self._features[self.add_total_matches] = True
    

    def add_total_points(self, year_index: int = 0) -> None:
        """
        Para o DataFrame em self._datas[year_index], adiciona:
         - TotalHomePoints: pontos do mandante obtidos em jogos anteriores (3 vitória, 1 empate, 0 derrota)
         - TotalAwayPoints: pontos do visitante obtidos em jogos anteriores
        """
        df = self._datas[year_index].copy()

        # 1) Calcular os pontos de casa e de fora para cada partida
        home_pts = df['FTR'].map({'H': 3, 'D': 1, 'A': 0})
        away_pts = df['FTR'].map({'A': 3, 'D': 1, 'H': 0})

        # 2) Criar visão “long” com cada time e seus pontos naquele jogo
        df_home = (
            df[['HomeTeam']]
            .rename(columns={'HomeTeam':'Team'})
            .assign(Points=home_pts,
                    match_id=df.index,
                    side='home',
                    event_id=df.index * 2)
        )
        df_away = (
            df[['AwayTeam']]
            .rename(columns={'AwayTeam':'Team'})
            .assign(Points=away_pts,
                    match_id=df.index,
                    side='away',
                    event_id=df.index * 2 + 1)
        )

        df_long = pd.concat([df_home, df_away], ignore_index=True)
        df_long = df_long.sort_values('event_id')

        # 3) Acumular cumulativamente e remover os pontos do jogo atual
        df_long['CumSum'] = df_long.groupby('Team')['Points'].cumsum()
        df_long['PrevPoints'] = df_long['CumSum'] - df_long['Points']

        # 4) Pivotar de volta para wide e atribuir ao DataFrame original
        pivot = df_long.pivot(index='match_id', columns='side', values='PrevPoints')
        df['TotalHomePoints'] = pivot['home'].fillna(0).astype(int).values
        df['TotalAwayPoints'] = pivot['away'].fillna(0).astype(int).values

        # 5) Atualiza o dataframe na lista interna
        self._datas[year_index] = df
        self._features[self.add_total_points] = True
    
    # ========================


    # Métricas derivadas
    def add_average_gols_scored(self, year_index: int = 0) -> None:
        """
        Para o DataFrame em self._datas[year_index], adiciona:
         - AverageHomeGoalsScored: média de gols marcados pelo mandante em jogos anteriores
         - AverageAwayGoalsScored: média de gols marcados pelo visitante em jogos anteriores
        """
        df = self._datas[year_index].copy()

        # Evita divisão por zero: cria colunas temporárias para denominar
        home_matches = df['TotalHomeMatches']
        away_matches = df['TotalAwayMatches']

        # cálculo das médias
        df['AverageHomeGoalsScored'] = np.where(
            home_matches > 0,
            df['TotalHomeGoals'] / home_matches,
            0.0
        )
        df['AverageAwayGoalsScored'] = np.where(
            away_matches > 0,
            df['TotalAwayGoals'] / away_matches,
            0.0
        )

        # atualiza o DataFrame interno
        self._datas[year_index] = df


    def add_average_gols_conceded(self, year_index: int = 0) -> None:
        """
        Para o DataFrame em self._datas[year_index], adiciona:
         - AverageHomeGoalsConceded: média de gols sofridos pelo mandante em jogos anteriores
         - AverageAwayGoalsConceded: média de gols sofridos pelo visitante em jogos anteriores
        """
        df = self._datas[year_index].copy()

        # evita divisão por zero pegando o total de jogos
        home_matches = df['TotalHomeMatches']
        away_matches = df['TotalAwayMatches']

        # cálculo das médias de gols sofridos
        df['AverageHomeGoalsConceded'] = np.where(
            home_matches > 0,
            df['TotalHomeConceded'] / home_matches,
            0.0
        )
        df['AverageAwayGoalsConceded'] = np.where(
            away_matches > 0,
            df['TotalAwayConceded'] / away_matches,
            0.0
        )

        # atualiza o DataFrame interno
        self._datas[year_index] = df


    def add_ppg(self, year_index: int = 0) -> None:
        """
        Para o DataFrame em self._datas[year_index], adiciona:
         - AverageHomePoints: média de pontos obtidos pelo mandante em jogos anteriores
         - AverageAwayPoints: média de pontos obtidos pelo visitante em jogos anteriores
        """
        df = self._datas[year_index].copy()

        # evita divisão por zero
        home_matches = df['TotalHomeMatches']
        away_matches = df['TotalAwayMatches']

        # cálculo de pontos por jogo
        df['AverageHomePoints'] = np.where(
            home_matches > 0,
            df['TotalHomePoints'] / home_matches,
            0.0
        )
        df['AverageAwayPoints'] = np.where(
            away_matches > 0,
            df['TotalAwayPoints'] / away_matches,
            0.0
        )

        # atualiza o DataFrame interno
        self._datas[year_index] = df
    
    # ========================


    # Métricas dos último N jogos
    def add_last_n_average_gols_scored(self, n: int, year_index: int = 0) -> None:
        """
        Para o DataFrame em self._datas[year_index], adiciona:
         - AverageHomeGoalsScoredLast{n}: média de gols marcados pelo mandante nos últimos n jogos
         - AverageAwayGoalsScoredLast{n}: média de gols marcados pelo visitante nos últimos n jogos
        (exclui o jogo atual; se houver menos de n jogos anteriores, faz a média sobre o disponível)
        """
        df = self._datas[year_index].copy()

        # Monta visão “long”
        df_home = (
            df[['HomeTeam', 'FTHG']]
            .rename(columns={'HomeTeam': 'Team', 'FTHG': 'Goals'})
            .assign(match_id=df.index, side='home', event_id=df.index * 2)
        )
        df_away = (
            df[['AwayTeam', 'FTAG']]
            .rename(columns={'AwayTeam': 'Team', 'FTAG': 'Goals'})
            .assign(match_id=df.index, side='away', event_id=df.index * 2 + 1)
        )
        df_long = pd.concat([df_home, df_away], ignore_index=True)
        df_long = df_long.sort_values('event_id').reset_index(drop=True)

        # Calcula a média móvel dos últimos n jogos, excluindo o atual
        df_long['RollingAvg'] = (
            df_long
            .groupby('Team')['Goals']
            .transform(lambda x: x.shift().rolling(window=n, min_periods=1).mean())
        )

        # Pivot de volta para wide
        pivot = df_long.pivot(index='match_id', columns='side', values='RollingAvg')

        # Atribui ao DataFrame original
        df[f'AverageHomeGoalsScoredLast{n}'] = pivot['home'].reindex(df.index).fillna(0).values
        df[f'AverageAwayGoalsScoredLast{n}'] = pivot['away'].reindex(df.index).fillna(0).values

        # Atualiza o DataFrame interno
        self._datas[year_index] = df


    # ========================


model = Preprocessing()
model._load_data()


print(model.datas[0].head())

print('\n========\n')

# Aplica o método ao primeiro ano
# model.datas[0].iloc[:, [2, 3]] = 1
# model.datas[0].iloc[:, 4] = 'D'
model.add_total_matches(0)
model.add_goals_scored(0)
model.add_goals_conceded(0)
model.add_total_points(0)
model.add_average_gols_scored(0)
model.add_average_gols_conceded(0)
model.add_ppg(0)
model.add_last_n_average_gols_scored(5, 0)


# Depois: têm as colunas TotalHomeGoals e TotalAwayGoals
print(model.datas[0])
model.datas[0].to_csv('teste.csv', sep=',', index=False)