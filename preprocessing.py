import pandas as pd
import numpy as np
from utils import Season
from sklearn.preprocessing import LabelEncoder

class Preprocessing:

    DATA_PATH = './cleaned_data'
    PRUNING = 120 # 120


    def __init__(self):
        self._datas: list[pd.DataFrame] = []
        self._export: pd.DataFrame = None

        self._features = {
            self._add_goals_scored: False,
            self._add_goals_conceded: False,
            self._add_total_matches: False,
            self._add_total_points: False,
            self._add_average_gols_scored: False,
            self._add_average_gols_conceded: False,
            self._add_ppg: False,
            self._add_last_n_average_gols_scored: False,
            self._add_last_n_average_gols_conceded: False,
            self._add_last_n_ppg: False
        }

    def _load_data(self) -> None:
        season = Season(14, 15) # 23, 24

        while season.next():
            if season.date == '2021':
                print('pulou 2021!')
                continue
            file_name = f'{Preprocessing.DATA_PATH}/{season.date}.csv'
            df = pd.read_csv(file_name, sep=',')
            df = df.dropna(subset=['FTR'])
            self._datas.append(df)
            print(len(self._datas))


    @property
    def export(self):
        """Getter method"""
        return self._export

    @property
    def datas(self):
        """Getter method"""
        return self._datas
    

    @datas.setter
    def datas(self, value: list[pd.DataFrame]) -> None:
        """Setter method"""
        self._datas = value

    # Métricas base
    def _add_goals_scored(self) -> None:
        """
        Para o DataFrame em self._datas[year_index], adiciona:
         - TotalHomeGoals: total de gols que o time mandante fez antes deste jogo
         - TotalAwayGoals: total de gols que o time visitante fez antes deste jogo
        """

        for year_index in range(len(self._datas)):
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


    def _add_goals_conceded(self) -> None:
        """
        Para o DataFrame em self._datas[year_index], adiciona:
         - TotalHomeConceded: gols sofridos pelo mandante em jogos anteriores
         - TotalAwayConceded: gols sofridos pelo visitante em jogos anteriores
        """

        for year_index in range(len(self._datas)):
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


    def _add_total_matches(self) -> None:
        """
        Para o DataFrame em self._datas[year_index], adiciona:
         - TotalHomeMatches: quantidade de partidas já jogadas pelo mandante antes deste jogo
         - TotalAwayMatches: quantidade de partidas já jogadas pelo visitante antes deste jogo
        """

        for year_index in range(len(self._datas)):
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
    

    def _add_total_points(self) -> None:
        """
        Para o DataFrame em self._datas[year_index], adiciona:
         - TotalHomePoints: pontos do mandante obtidos em jogos anteriores (3 vitória, 1 empate, 0 derrota)
         - TotalAwayPoints: pontos do visitante obtidos em jogos anteriores
        """

        for year_index in range(len(self._datas)):
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
    
    # ========================


    # Métricas derivadas
    def _add_average_gols_scored(self) -> None:
        """
        Para o DataFrame em self._datas[year_index], adiciona:
         - AverageHomeGoalsScored: média de gols marcados pelo mandante em jogos anteriores
         - AverageAwayGoalsScored: média de gols marcados pelo visitante em jogos anteriores
        """

        for year_index in range(len(self._datas)):
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


    def _add_average_gols_conceded(self, year_index: int = 0) -> None:
        """
        Para o DataFrame em self._datas[year_index], adiciona:
         - AverageHomeGoalsConceded: média de gols sofridos pelo mandante em jogos anteriores
         - AverageAwayGoalsConceded: média de gols sofridos pelo visitante em jogos anteriores
        """

        for year_index in range(len(self._datas)):
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


    def _add_ppg(self) -> None:
        """
        Para o DataFrame em self._datas[year_index], adiciona:
         - AverageHomePoints: média de pontos obtidos pelo mandante em jogos anteriores
         - AverageAwayPoints: média de pontos obtidos pelo visitante em jogos anteriores
        """

        for year_index in range(len(self._datas)):
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
    def _add_last_n_average_gols_scored(self, n: int) -> None:
        """
        Para o DataFrame em self._datas[year_index], adiciona:
         - AverageHomeGoalsScoredLast{n}: média de gols marcados pelo mandante nos últimos n jogos
         - AverageAwayGoalsScoredLast{n}: média de gols marcados pelo visitante nos últimos n jogos
        (exclui o jogo atual; se houver menos de n jogos anteriores, faz a média sobre o disponível)
        """

        for year_index in range(len(self._datas)):
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


    def _add_last_n_average_gols_conceded(self, n: int) -> None:
        """
        Para o DataFrame em self._datas[year_index], adiciona:
         - AverageHomeGoalsConcededLast{n}: média de gols sofridos pelo mandante nos últimos n jogos
         - AverageAwayGoalsConcededLast{n}: média de gols sofridos pelo visitante nos últimos n jogos
        (exclui o jogo atual; se houver menos de n jogos anteriores, faz a média sobre o disponível)
        """

        for year_index in range(len(self._datas)):
            df = self._datas[year_index].copy()

            # Monta visão “long” de gols sofridos
            df_home = (
                df[['HomeTeam', 'FTAG']]
                .rename(columns={'HomeTeam': 'Team', 'FTAG': 'Goals'})
                .assign(match_id=df.index, side='home', event_id=df.index * 2)
            )
            df_away = (
                df[['AwayTeam', 'FTHG']]
                .rename(columns={'AwayTeam': 'Team', 'FTHG': 'Goals'})
                .assign(match_id=df.index, side='away', event_id=df.index * 2 + 1)
            )
            df_long = pd.concat([df_home, df_away], ignore_index=True)
            df_long = df_long.sort_values('event_id').reset_index(drop=True)

            # Calcula média móvel de gols sofridos nos últimos n jogos, excluindo o atual
            df_long['RollingAvgConceded'] = (
                df_long
                .groupby('Team')['Goals']
                .transform(lambda x: x.shift().rolling(window=n, min_periods=1).mean())
            )

            # Pivot de volta para o formato wide
            pivot = df_long.pivot(index='match_id', columns='side', values='RollingAvgConceded')

            # Atribui as colunas ao DataFrame original
            df[f'AverageHomeGoalsConcededLast{n}'] = pivot['home'].reindex(df.index).fillna(0).values
            df[f'AverageAwayGoalsConcededLast{n}'] = pivot['away'].reindex(df.index).fillna(0).values

            # Atualiza o DataFrame na lista interna
            self._datas[year_index] = df


    def _add_last_n_ppg(self, n: int) -> None:
        """
        Para o DataFrame em self._datas[year_index], adiciona:
         - AverageHomePointsLast{n}: média de pontos obtidos pelo mandante nos últimos n jogos
         - AverageAwayPointsLast{n}: média de pontos obtidos pelo visitante nos últimos n jogos
        (exclui o jogo atual; se houver menos de n jogos anteriores, faz a média sobre o disponível)
        """

        for year_index in range(len(self._datas)):
            df = self._datas[year_index].copy()

            # 1) Calcula pontos ganhos em cada partida (3/1/0)
            home_pts = df['FTR'].map({'H': 3, 'D': 1, 'A': 0})
            away_pts = df['FTR'].map({'A': 3, 'D': 1, 'H': 0})

            # 2) Monta visão “long” com cada evento de pontuação
            df_home = (
                df[['HomeTeam']]
                .rename(columns={'HomeTeam': 'Team'})
                .assign(Points=home_pts,
                        match_id=df.index,
                        side='home',
                        event_id=df.index * 2)
            )
            df_away = (
                df[['AwayTeam']]
                .rename(columns={'AwayTeam': 'Team'})
                .assign(Points=away_pts,
                        match_id=df.index,
                        side='away',
                        event_id=df.index * 2 + 1)
            )
            df_long = pd.concat([df_home, df_away], ignore_index=True)
            df_long = df_long.sort_values('event_id').reset_index(drop=True)

            # 3) Calcula média móvel de pontos nos últimos n jogos, excluindo o atual
            df_long['RollingAvgPoints'] = (
                df_long
                .groupby('Team')['Points']
                .transform(lambda x: x.shift().rolling(window=n, min_periods=1).mean())
            )

            # 4) Pivot de volta para wide
            pivot = df_long.pivot(index='match_id', columns='side', values='RollingAvgPoints')

            # 5) Atribui ao DataFrame original e preenche zeros onde não houver histórico
            df[f'AverageHomePointsLast{n}'] = pivot['home'].reindex(df.index).fillna(0).values
            df[f'AverageAwayPointsLast{n}'] = pivot['away'].reindex(df.index).fillna(0).values

            # 6) Atualiza o DataFrame interno
            self._datas[year_index] = df


    def _codificar_times(self) -> None:
        """
        Para o DataFrame em self._datas[year_index], aplica label encoding
        em HomeTeam e AwayTeam, criando duas colunas:
         - HomeTeamEnc
         - AwayTeamEnc
        """
        
        encoder = LabelEncoder()

        # 1) Ajusta o encoder no conjunto de todas as equipes (casa + visitante)
        all_teams = pd.concat([
            self._export['HomeTeam'],
            self._export['AwayTeam']
        ],  ignore_index=True)

        encoder.fit(all_teams)

        # faz mapeamento
        mapping = {
            team: int(code)
            for team, code in zip(encoder.classes_, encoder.transform(encoder.classes_))
        }
        print("Team encoding mapping:")
        for team, code in mapping.items():
            print(f"  {team}: {code}")

        # 2) Transforma cada coluna usando o mesmo encoder
        self._export['HomeTeamEnc'] = encoder.transform(
            self._export['HomeTeam']
        )

        self._export['AwayTeamEnc'] = encoder.transform(
            self._export['AwayTeam']
        )

        print(self._export)

    # ========================

    def _pruning(self, n: int) -> None:
        for df in self._datas:
            df.drop(index=df.index[:n], inplace=True)
            df.reset_index(drop=True, inplace=True)
        

    def _merge(self) -> None:
        self._export = pd.concat(self._datas, ignore_index=True)


    def export_data(self) -> None:
        self._load_data()

        self._add_total_matches()
        self._add_goals_scored()
        self._add_goals_conceded()
        self._add_total_points()
        self._add_average_gols_scored()
        self._add_average_gols_conceded()
        self._add_ppg()
        self._add_last_n_average_gols_scored(6)
        self._add_last_n_average_gols_conceded(6)
        self._add_last_n_ppg(6)
        self._pruning(Preprocessing.PRUNING)
        self._merge()
        self._export.to_csv('real.csv', sep=',', index=False)
        self._codificar_times()
        self._export.to_csv('codificados.csv', sep=',', index=False)

        selected_features = [
            'HomeTeamEnc',
            'AwayTeamEnc',
            #'TotalHomeMatches',
            #'TotalAwayMatches',
            'TotalHomeGoals',
            'TotalAwayGoals',
            'TotalHomeConceded',
            'TotalAwayConceded',
            #'AverageHomeGoalsScored',
            #'AverageAwayGoalsScored',
            #'AverageHomeGoalsConceded',
            #'AverageAwayGoalsConceded',
            #'AverageHomePoints',
            #'AverageAwayPoints',
            'TotalHomePoints',
            'TotalAwayPoints',
            #'AverageHomeGoalsScoredLast6',
            #'AverageAwayGoalsScoredLast6',
            #'AverageHomeGoalsConcededLast6',
            #'AverageAwayGoalsConcededLast6',
            #'AverageHomePointsLast6',
            #'AverageAwayPointsLast6',
            'FTR'
        ]

        self._export = self._export.loc[:, selected_features]

        

       


#model = Preprocessing()
#model.export_data()
#model._export.to_csv('teste.csv', sep=',', index=False)