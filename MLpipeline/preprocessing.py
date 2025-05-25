import pandas as pd
import numpy as np
from MLpipeline.utils import Season
from sklearn.preprocessing import LabelEncoder

class Preprocessing:

    DATA_PATH = './cleaned_data'
    PRUNING = 120 # 120


    def __init__(self):
        self._datas: list[pd.DataFrame] = []
        self._export: pd.DataFrame = None
        self._encoding_table: dict = {}

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
            file_name = f'{Preprocessing.DATA_PATH}/{season.date}.csv'
            df = pd.read_csv(file_name, sep=',')
            df = df.dropna(subset=['FTR'])
            self._datas.append(df)


    def __load_data_temp(self) -> list[pd.DataFrame]:
        season = Season(93, 94) # 23, 24
        dataframes: list[pd.DataFrame] = []

        while season.next():
            file_name = f'{Preprocessing.DATA_PATH}/{season.date}.csv'
            df = pd.read_csv(file_name, sep=',')
            df = df.dropna(subset=['FTR'])
            dataframes.append(df)

        return dataframes


    def _add_average_historical_points(self) -> None:
        """
        Para cada DataFrame em self._datas, adiciona duas colunas:
         - HistoricalAvgHomePoints: média de pontos de temporada histórica do mandante
         - HistoricalAvgAwayPoints: média de pontos de temporada histórica do visitante
        A média é calculada por time, usando todas as temporadas carregadas por __load_data_temp()
        que ocorreram antes da temporada da própria DataFrame.
        """
        # 1) Carrega todas as temporadas históricas em ordem cronológica
        hist_raw = self.__load_data_temp()  # lista de DataFrames de 1992-93 até última temporada
        M = len(hist_raw)
        N = len(self._datas)

        # 2) Para cada temporada histórica, computa total de pontos por time
        records = []
        for season_idx, df_hist in enumerate(hist_raw):
            # calcula pontos por jogo
            home_pts = df_hist['FTR'].map({'H': 3, 'D': 1, 'A': 0})
            away_pts = df_hist['FTR'].map({'A': 3, 'D': 1, 'H': 0})

            # concatena e soma por time
            df_h = pd.DataFrame({'Team': df_hist['HomeTeam'], 'Points': home_pts})
            df_a = pd.DataFrame({'Team': df_hist['AwayTeam'], 'Points': away_pts})
            df_comb = pd.concat([df_h, df_a], ignore_index=True)
            total_by_team = df_comb.groupby('Team')['Points'].sum().reset_index()
            total_by_team['SeasonIdx'] = season_idx

            records.append(total_by_team)

        hist_points_df = pd.concat(records, ignore_index=True)
        # hist_points_df tem colunas ['Team', 'Points', 'SeasonIdx']

        # 3) Para cada DataFrame alvo em self._datas, calcula média histórica
        #    expurgando temporadas futuras (incluindo a própria)
        start_idx = M - N  # index na lista histórica correspondente ao primeiro df de self._datas
        for i, df in enumerate(self._datas):
            season_idx = start_idx + i

            # filtra apenas temporadas anteriores
            past = hist_points_df[hist_points_df['SeasonIdx'] < season_idx]
            # calcula média de pontos por time
            avg_past = past.groupby('Team')['Points'].mean()

            # mapeia para as colunas home e away, preenchendo 0 se time não existir no histórico
            df['HistoricalAvgHomePoints'] = df['HomeTeam'].map(avg_past).fillna(0.0)
            df['HistoricalAvgAwayPoints'] = df['AwayTeam'].map(avg_past).fillna(0.0)

            # atualiza na lista interna
            self._datas[i] = df

        

    @property
    def export(self):
        """Getter method"""
        return self._export


    @property
    def datas(self):
        """Getter method"""
        return self._datas
    

    @property
    def encoding_table(self) -> dict:
        """Getter method"""
        return self._encoding_table


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

        # tabela de mapeamento:
        for team, code in mapping.items():
            self._encoding_table[team] = code

        


        # 2) Transforma cada coluna usando o mesmo encoder
        self._export['HomeTeamEnc'] = encoder.transform(
            self._export['HomeTeam']
        )

        self._export['AwayTeamEnc'] = encoder.transform(
            self._export['AwayTeam']
        )

    # ========================

    def _pruning(self, n: int) -> None:
        for df in self._datas:
            df.drop(index=df.index[:n], inplace=True)
            df.reset_index(drop=True, inplace=True)
        

    def _merge(self) -> None:
        self._export = pd.concat(self._datas, ignore_index=True)

    def _merge_temp(self, list_df: list[pd.DataFrame]) -> None:
        return pd.concat(list_df, ignore_index=True)


    def _add_is_it_elite(self) -> None:
        """
        Adiciona colunas booleanas indicando se o time da casa ou visitante
        é um "time estrela" (elite) historicamente forte.
         - IsItEliteHome: 1 se HomeTeam estiver em elite_teams, 0 caso contrário
         - IsItEliteAway: 1 se AwayTeam estiver em elite_teams, 0 caso contrário
        """
        elite_teams = {
            "Man City",
            "Man United",
            "Arsenal",
            "Liverpool",
            "Chelsea",
            "Tottenham",
        }

        for i, df in enumerate(self._datas):
            # marca 1/0 se o time faz parte da lista de elites
            df['IsItEliteHome'] = df['HomeTeam'].isin(elite_teams).astype(int)
            df['IsItEliteAway'] = df['AwayTeam'].isin(elite_teams).astype(int)
            # atualiza o DataFrame na lista
            self._datas[i] = df


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
        self._add_average_historical_points()
        self._add_is_it_elite()
        self._pruning(Preprocessing.PRUNING)
        self._merge()
        self._export.to_csv('real.csv', sep=',', index=False)
        self._codificar_times()
        self._export.to_csv('codificados.csv', sep=',', index=False)

        selected_features = [
            'HomeTeamEnc',
            'AwayTeamEnc',
            'FTHG',
            'FTAG',
            'TotalHomeMatches',
            'TotalAwayMatches',
            'TotalHomeGoals',
            'TotalAwayGoals',
            'TotalHomeConceded',
            'TotalAwayConceded',
            'AverageHomeGoalsScored',
            'AverageAwayGoalsScored',
            'AverageHomeGoalsConceded',
            'AverageAwayGoalsConceded',
            'AverageHomePoints',
            'AverageAwayPoints',
            'TotalHomePoints',
            'TotalAwayPoints',
            'AverageHomeGoalsScoredLast6',
            'AverageAwayGoalsScoredLast6',
            'AverageHomeGoalsConcededLast6',
            'AverageAwayGoalsConcededLast6',
            'AverageHomePointsLast6',
            'AverageAwayPointsLast6',
            'IsItEliteHome',
            'IsItEliteAway',
            'HistoricalAvgHomePoints',
            'HistoricalAvgAwayPoints',
            'FTR'
        ]

        self._export = self._export.loc[:, selected_features]
     

class Search:
    def __init__(self, encoding_table: dict, data: pd.DataFrame):
        """
        encoding_table: um dicionário que mapeia o nome do time ao
        seu código de encoding. Por exemplo, 
        encoding_table['Arsenal'] retorna um inteiro.
        """
        self._encoding_table = encoding_table
        self._data = data


    def search_total_points(self, team: str | int) -> int:
        """
        Retorna o total de pontos do último jogo do time, já incluindo os pontos do próprio jogo:
        - pega TotalHomePoints ou TotalAwayPoints da última linha;
        - adiciona 3 pontos se vitória (H para casa, A para visitante);
        - adiciona 1 ponto em caso de empate (D);
        - soma e retorna.
        """
        # 1) Converte nome → código, se necessário
        if isinstance(team, str):
            if team not in self._encoding_table:
                raise KeyError(f"Time '{team}' não está na tabela de encoding.")
            code = self._encoding_table[team]
        else:
            code = team

        # 2) Máscaras para jogos em casa ou fora
        mask_home = self._data['HomeTeamEnc'] == code
        mask_away = self._data['AwayTeamEnc'] == code
        mask = mask_home | mask_away

        # 3) Verifica existência
        if not mask.any():
            raise ValueError(f"Time (código {code}) não encontrado no DataFrame.")

        # 4) Pega última linha
        last_match = self._data[mask].iloc[-1]

        # 5) Pontos acumulados até antes do jogo
        if last_match['HomeTeamEnc'] == code:
            base_points = int(last_match['TotalHomePoints'])
            is_home = True
        else:
            base_points = int(last_match['TotalAwayPoints'])
            is_home = False

        # 6) Pontos do jogo atual, pelo FTR
        ftr = last_match['FTR']
        if ftr == 'D':
            extra = 1
        elif is_home and ftr == 'H':
            extra = 3
        elif (not is_home) and ftr == 'A':
            extra = 3
        else:
            extra = 0

        return base_points + extra


    def search_total_matches(self, team: str | int) -> int:
        """
        Retorna o total de partidas do time, já incluindo o jogo atual:
        - pega TotalHomeMatches ou TotalAwayMatches da última linha;
        - adiciona 1 pela partida corrente.
        """
        # 1) Converte nome → código, se necessário
        if isinstance(team, str):
            if team not in self._encoding_table:
                raise KeyError(f"Time '{team}' não está na tabela de encoding.")
            code = self._encoding_table[team]
        else:
            code = team

        # 2) Máscaras para jogos em casa ou fora
        mask_home = self._data['HomeTeamEnc'] == code
        mask_away = self._data['AwayTeamEnc'] == code
        mask = mask_home | mask_away

        # 3) Verifica existência
        if not mask.any():
            raise ValueError(f"Time (código {code}) não encontrado no DataFrame.")

        # 4) Pega última linha
        last_match = self._data[mask].iloc[-1]

        # 5) Total de partidas até antes do jogo
        if last_match['HomeTeamEnc'] == code:
            base_matches = int(last_match['TotalHomeMatches'])
        else:
            base_matches = int(last_match['TotalAwayMatches'])

        # 6) Soma a partida corrente
        return base_matches + 1


    def search_total_goals(self, team: str | int) -> int:
        """
        Retorna o total de gols marcados pelo time no campeonato, já incluindo os gols do jogo atual:
        - pega TotalHomeGoals ou TotalAwayGoals da última linha;
        - adiciona FTHG (se jogou em casa) ou FTAG (se jogou fora) da mesma linha.
        """
        # 1) Converte nome → código, se necessário
        if isinstance(team, str):
            if team not in self._encoding_table:
                raise KeyError(f"Time '{team}' não está na tabela de encoding.")
            code = self._encoding_table[team]
        else:
            code = team

        # 2) Máscaras para jogos em casa ou fora
        mask_home = self._data['HomeTeamEnc'] == code
        mask_away = self._data['AwayTeamEnc'] == code
        mask = mask_home | mask_away

        # 3) Verifica existência do time no DataFrame
        if not mask.any():
            raise ValueError(f"Time (código {code}) não encontrado no DataFrame.")

        # 4) Seleciona a última partida
        last_match = self._data[mask].iloc[-1]

        # 5) Gols acumulados até antes do jogo
        if last_match['HomeTeamEnc'] == code:
            base_goals = int(last_match['TotalHomeGoals'])
            extra_goals = int(last_match['FTHG'])
        else:
            base_goals = int(last_match['TotalAwayGoals'])
            extra_goals = int(last_match['FTAG'])

        # 6) Retorna soma dos gols anteriores com os do jogo atual
        return base_goals + extra_goals


    def search_total_conceded(self, team: str | int) -> int:
        """
        Retorna o total de gols sofridos pelo time no campeonato, já incluindo os gols do jogo atual:
        - pega TotalHomeConceded ou TotalAwayConceded da última linha;
        - adiciona FTAG (se jogou em casa) ou FTHG (se jogou fora) da mesma linha.
        """
        # 1) Converte nome → código, se necessário
        if isinstance(team, str):
            if team not in self._encoding_table:
                raise KeyError(f"Time '{team}' não está na tabela de encoding.")
            code = self._encoding_table[team]
        else:
            code = team

        # 2) Máscaras para jogos em casa ou fora
        mask_home = self._data['HomeTeamEnc'] == code
        mask_away = self._data['AwayTeamEnc'] == code
        mask = mask_home | mask_away

        # 3) Verifica existência do time no DataFrame
        if not mask.any():
            raise ValueError(f"Time (código {code}) não encontrado no DataFrame.")

        # 4) Seleciona a última partida
        last_match = self._data[mask].iloc[-1]

        # 5) Gols sofridos acumulados até antes do jogo
        if last_match['HomeTeamEnc'] == code:
            base_conceded = int(last_match['TotalHomeConceded'])
            extra_conceded = int(last_match['FTAG'])
        else:
            base_conceded = int(last_match['TotalAwayConceded'])
            extra_conceded = int(last_match['FTHG'])

        # 6) Retorna soma dos gols sofridos anteriores com os do jogo atual
        return base_conceded + extra_conceded


    def average_goals_scored(self, team: str | int) -> float:
        """
        Retorna a média de gols marcados pelo time no campeonato, já incluindo os gols do jogo atual:
        - pega AverageHomeGoalsScored ou AverageAwayGoalsScored da última linha;
        - calcula o total de gols anteriores: base_avg * base_matches;
        - soma os gols do jogo atual (FTHG se em casa, FTAG se fora);
        - divide pelo número de partidas anterior + 1.
        """
        # 1) Converte nome → código, se necessário
        if isinstance(team, str):
            if team not in self._encoding_table:
                raise KeyError(f"Time '{team}' não está na tabela de encoding.")
            code = self._encoding_table[team]
        else:
            code = team

        # 2) Máscaras para jogos em casa ou fora
        mask_home = self._data['HomeTeamEnc'] == code
        mask_away = self._data['AwayTeamEnc'] == code
        mask = mask_home | mask_away

        # 3) Verifica existência do time no DataFrame
        if not mask.any():
            raise ValueError(f"Time (código {code}) não encontrado no DataFrame.")

        # 4) Seleciona a última partida
        last_match = self._data[mask].iloc[-1]

        # 5) Extrai média e número de partidas anteriores
        if last_match['HomeTeamEnc'] == code:
            base_avg = float(last_match['AverageHomeGoalsScored'])
            base_matches = int(last_match['TotalHomeMatches'])
            extra_goals = int(last_match['FTHG'])
        else:
            base_avg = float(last_match['AverageAwayGoalsScored'])
            base_matches = int(last_match['TotalAwayMatches'])
            extra_goals = int(last_match['FTAG'])

        # 6) Recalcula média incluindo o jogo atual
        total_goals_prev = base_avg * base_matches
        new_total_goals = total_goals_prev + extra_goals
        new_matches = base_matches + 1

        return new_total_goals / new_matches


    def average_goals_conceded(self, team: str | int) -> float:
        """
        Retorna a média de gols sofridos pelo time no campeonato, já incluindo os gols do jogo atual:
        - pega AverageHomeGoalsConceded ou AverageAwayGoalsConceded da última linha;
        - calcula o total de gols sofridos anteriores: base_avg * base_matches;
        - soma os gols sofridos no jogo atual (FTAG se em casa, FTHG se fora);
        - divide pelo número de partidas anterior + 1.
        """
        # 1) Converte nome → código, se necessário
        if isinstance(team, str):
            if team not in self._encoding_table:
                raise KeyError(f"Time '{team}' não está na tabela de encoding.")
            code = self._encoding_table[team]
        else:
            code = team

        # 2) Máscaras para jogos em casa ou fora
        mask_home = self._data['HomeTeamEnc'] == code
        mask_away = self._data['AwayTeamEnc'] == code
        mask = mask_home | mask_away

        # 3) Verifica existência do time no DataFrame
        if not mask.any():
            raise ValueError(f"Time (código {code}) não encontrado no DataFrame.")

        # 4) Seleciona a última partida
        last_match = self._data[mask].iloc[-1]

        # 5) Extrai média de gols sofridos e número de partidas anteriores
        if last_match['HomeTeamEnc'] == code:
            base_avg = float(last_match['AverageHomeGoalsConceded'])
            base_matches = int(last_match['TotalHomeMatches'])
            extra_conceded = int(last_match['FTAG'])
        else:
            base_avg = float(last_match['AverageAwayGoalsConceded'])
            base_matches = int(last_match['TotalAwayMatches'])
            extra_conceded = int(last_match['FTHG'])

        # 6) Recalcula média incluindo o jogo atual
        total_conceded_prev = base_avg * base_matches
        new_total_conceded = total_conceded_prev + extra_conceded
        new_matches = base_matches + 1

        return new_total_conceded / new_matches


    def average_points(self, team: str | int) -> float:
        """
        Retorna a média de pontos por partida do time no campeonato, já incluindo os pontos do jogo atual:
        - pega TotalHomePoints ou TotalAwayPoints da última linha;
        - pega TotalHomeMatches ou TotalAwayMatches da última linha;
        - calcula os pontos extra do jogo atual (3 por vitória, 1 por empate);
        - soma e divide pelo número de partidas + 1.
        """
        # 1) Converte nome → código, se necessário
        if isinstance(team, str):
            if team not in self._encoding_table:
                raise KeyError(f"Time '{team}' não está na tabela de encoding.")
            code = self._encoding_table[team]
        else:
            code = team

        # 2) Máscaras para jogos em casa ou fora
        mask_home = self._data['HomeTeamEnc'] == code
        mask_away = self._data['AwayTeamEnc'] == code
        mask = mask_home | mask_away

        # 3) Verifica existência do time no DataFrame
        if not mask.any():
            raise ValueError(f"Time (código {code}) não encontrado no DataFrame.")

        # 4) Seleciona a última partida
        last_match = self._data[mask].iloc[-1]

        # 5) Extrai pontos e partidas acumulados até antes do jogo
        if last_match['HomeTeamEnc'] == code:
            base_points = int(last_match['TotalHomePoints'])
            base_matches = int(last_match['TotalHomeMatches'])
            is_home = True
        else:
            base_points = int(last_match['TotalAwayPoints'])
            base_matches = int(last_match['TotalAwayMatches'])
            is_home = False

        # 6) Calcula pontos do jogo atual via FTR
        ftr = last_match['FTR']
        if ftr == 'D':
            extra = 1
        elif is_home and ftr == 'H':
            extra = 3
        elif (not is_home) and ftr == 'A':
            extra = 3
        else:
            extra = 0

        # 7) Recalcula média incluindo o jogo atual
        total_points = base_points + extra
        total_matches = base_matches + 1

        return total_points / total_matches


    def average_goals_scored_last_n(self, team: str | int, n: int) -> float:
        """
        Retorna a média de gols marcados pelo time nos últimos n jogos (incluindo o mais recente):
        - Seleciona as últimas n partidas do time (casa ou fora).
        - Para cada partida, soma FTHG se jogou em casa, ou FTAG se jogou fora.
        - Divide o total de gols por n e retorna o resultado.
        """
        # 1) Valida n
        if n <= 0:
            raise ValueError(f"O parâmetro n deve ser maior que zero, recebeu {n}.")

        # 2) Converte nome → código, se necessário
        if isinstance(team, str):
            if team not in self._encoding_table:
                raise KeyError(f"Time '{team}' não está na tabela de encoding.")
            code = self._encoding_table[team]
        else:
            code = team

        # 3) Máscara para jogos em casa ou fora
        mask_home = self._data['HomeTeamEnc'] == code
        mask_away = self._data['AwayTeamEnc'] == code
        df_team = self._data[mask_home | mask_away]

        # 4) Verifica se há jogos suficientes
        total_matches = len(df_team)
        if total_matches < n:
            raise ValueError(f"Time (código {code}) tem apenas {total_matches} jogos, menos que {n}.")

        # 5) Seleciona as últimas n partidas
        recent = df_team.iloc[-n:]

        # 6) Soma gols marcados em cada partida
        total_goals = 0
        for _, match in recent.iterrows():
            if match['HomeTeamEnc'] == code:
                total_goals += int(match['FTHG'])
            else:
                total_goals += int(match['FTAG'])

        # 7) Calcula e retorna a média
        return total_goals / n


    def average_goals_conceded_last_n(self, team: str | int, n: int) -> float:
        """
        Retorna a média de gols sofridos pelo time nas últimas n partidas:
        - Seleciona as últimas n partidas do time (casa ou fora).
        - Para cada partida, soma FTAG se jogou em casa, ou FTHG se jogou fora.
        - Divide o total de gols sofridos por n e retorna o resultado.
        """
        # 1) Valida n
        if n <= 0:
            raise ValueError(f"O parâmetro n deve ser maior que zero, recebeu {n}.")

        # 2) Converte nome → código, se necessário
        if isinstance(team, str):
            if team not in self._encoding_table:
                raise KeyError(f"Time '{team}' não está na tabela de encoding.")
            code = self._encoding_table[team]
        else:
            code = team

        # 3) Máscaras para jogos em casa ou fora
        mask_home = self._data['HomeTeamEnc'] == code
        mask_away = self._data['AwayTeamEnc'] == code
        df_team = self._data[mask_home | mask_away]

        # 4) Verifica se há jogos suficientes
        total_matches = len(df_team)
        if total_matches < n:
            raise ValueError(f"Time (código {code}) tem apenas {total_matches} jogos, menos que {n}.")

        # 5) Seleciona as últimas n partidas
        recent = df_team.iloc[-n:]

        # 6) Soma gols sofridos em cada partida
        total_conceded = 0
        for _, match in recent.iterrows():
            if match['HomeTeamEnc'] == code:
                total_conceded += int(match['FTAG'])
            else:
                total_conceded += int(match['FTHG'])

        # 7) Calcula e retorna a média
        return total_conceded / n


    
    def average_points_last_n(self, team: str | int, n: int) -> float:
        """
        Retorna a média de pontos por partida do time nas últimas n partidas:
        - Seleciona as últimas n partidas do time (casa ou fora).
        - Para cada partida:
            * se jogou em casa e FTR == 'H' → +3; se 'D' → +1; senão +0;
            * se jogou fora e FTR == 'A' → +3; se 'D' → +1; senão +0.
        - Divide o total de pontos por n e retorna o resultado.
        """
        # 1) Valida n
        if n <= 0:
            raise ValueError(f"O parâmetro n deve ser maior que zero, recebeu {n}.")

        # 2) Converte nome → código, se necessário
        if isinstance(team, str):
            if team not in self._encoding_table:
                raise KeyError(f"Time '{team}' não está na tabela de encoding.")
            code = self._encoding_table[team]
        else:
            code = team

        # 3) Filtra partidas do time
        mask_home = self._data['HomeTeamEnc'] == code
        mask_away = self._data['AwayTeamEnc'] == code
        df_team = self._data[mask_home | mask_away]

        # 4) Verifica se há jogos suficientes
        total_matches = len(df_team)
        if total_matches < n:
            raise ValueError(f"Time (código {code}) tem apenas {total_matches} jogos, menos que {n}.")

        # 5) Seleciona as últimas n partidas
        recent = df_team.iloc[-n:]

        # 6) Soma pontos em cada partida
        total_points = 0
        for _, match in recent.iterrows():
            ftr = match['FTR']
            if match['HomeTeamEnc'] == code:
                # jogo em casa
                if ftr == 'H':
                    total_points += 3
                elif ftr == 'D':
                    total_points += 1
            else:
                # jogo fora
                if ftr == 'A':
                    total_points += 3
                elif ftr == 'D':
                    total_points += 1

        # 7) Retorna média de pontos
        return total_points / n


    
    def is_it_elite(self, team: str) -> bool:
        # 1) Converte nome → código, se necessário
        elite_teams = [
            'Man City',
            'Liverpool',
            'Arsenal',
            'Tottenham',
            'Man United',
            'Chelsea'
        ]

        if team in elite_teams:
            return True
        
        return False




