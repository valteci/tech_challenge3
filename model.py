from preprocessing import Preprocessing
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler  # ou MinMaxScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, accuracy_score
from lightgbm import LGBMClassifier, early_stopping, log_evaluation
from sklearn.metrics import classification_report, accuracy_score


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

        




# 1. Exporta os dados
preprocessing = Preprocessing()
preprocessing.export_data()
data = preprocessing.export
encoding_table = preprocessing.encoding_table
search = Search(data=data, encoding_table=encoding_table)

times = ['Liverpool', 'Arsenal', 'Man City', 'Newcastle', 'Chelsea', 'Aston Villa', "Nott'm Forest",
         'Brighton', 'Brentford', 'Fulham', 'Bournemouth', 'Crystal Palace',
         'Everton', 'Wolves', 'West Ham', 'Man United', 'Tottenham', 
         'Leicester', 'Ipswich', 'Southampton']

for time in times:
    print(time + ' - ' + str(search.average_points_last_n(time, 6)))


exit()

# Regressão logística
"""
# 2. Separa features e target
X = data.drop(columns=['FTR'])
y = data['FTR'].astype(str)

# 3. Split treino/teste
x_train, x_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    stratify=y,
    random_state=32463
)

# 4. Escalonamento (padronização)
scaler = MinMaxScaler()            # para normalização [0–1], use MinMaxScaler()
#scaler = StandardScaler()
x_train_scaled = scaler.fit_transform(x_train)
x_test_scaled  = scaler.transform(x_test)

# 5. Criação do modelo
model = LogisticRegression(
    solver='lbfgs',       # multinomial por padrão no sklearn >=1.7
    max_iter=1000,
    random_state=32463
)

# 6. Treinamento
model.fit(x_train_scaled, y_train)

# 7. Previsões
probs = model.predict_proba(x_test_scaled)
preds = model.predict(x_test_scaled)

# 8. Avaliação
loss = log_loss(y_test, probs)
acc  = accuracy_score(y_test, preds)

print(f"Log-loss: {loss:.4f}")
print(f"Acurácia: {acc:.4f}")


novo_jogo = {
    'HomeTeamEnc': 16,
    'AwayTeamEnc': 50,
    #'TotalHomeMatches': ,
    #'TotalAwayMatches': ,
    #'TotalHomeGoals': 46,
    #'TotalAwayGoals': 51,
    #'TotalHomeConceded': 48,
    #'TotalAwayConceded': 64,
    #'AverageHomeGoalsScored': ,
    #'AverageAwayGoalsScored': ,
    #'AverageHomeGoalsConceded': ,
    #'AverageAwayGoalsConceded': ,
    #'AverageHomePoints': ,
    #'AverageAwayPoints': ,
    'TotalHomePoints': 49,
    'TotalAwayPoints': 41,
    #'AverageHomeGoalsScoredLast6': ,
    #'AverageAwayGoalsScoredLast6': ,
    #'AverageHomeGoalsConcededLast6': ,
    #'AverageAwayGoalsConcededLast6': ,
    #'AverageHomePointsLast6': ,
    #'AverageAwayPointsLast6': ,
}

df_novo = pd.DataFrame([novo_jogo])

# 2) Aplica o mesmo MinMaxScaler usado no treinamento
df_novo_scaled = scaler.transform(df_novo)

# 3) Gera probabilidades e imprime
probs_novo = model.predict_proba(df_novo_scaled)[0]
for classe, p in zip(model.classes_, probs_novo):
    print(f"Probabilidade de {classe}: {p*100:.1f}%")


"""


# lightgbm
#"""
# 2. Separa features e target
X = data.drop(columns=['FTR'])
y = data['FTR'].astype(str)

# 3. Split treino/teste estratificado
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    stratify=y,
    random_state=42
)

# 4. Instancia o modelo LightGBM (boosted trees)
model = LGBMClassifier(
    objective='multiclass',
    num_class=3,
    boosting_type='gbdt',
    learning_rate=0.05,
    n_estimators=500,
    num_leaves=31,
    random_state=42
)

# 5. Treina com early stopping no conjunto de teste
model.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    eval_metric='multi_logloss',
    callbacks=[
        early_stopping(stopping_rounds=20),    # interrompe se não melhorar por 20 iters
        log_evaluation(period=50)],
)

# 6. Previsões e avaliação
probs = model.predict_proba(X_test)
preds = model.predict(X_test)

print(f"Log-loss: {log_loss(y_test, probs):.4f}")
print(f"Acurácia: {accuracy_score(y_test, preds):.4f}")


# 7. Matriz de confusão
report = classification_report(
    y_test, 
    preds,
    labels=model.classes_,        # garante a ordem ['H','D','A']
    target_names=model.classes_,  # nomes legíveis das classes
    digits=4                       # casas decimais
)
print("Classification Report:")
print(report)

# 2) Acurácia global (opcional, já aparece no report)
acc = accuracy_score(y_test, preds)
print(f"Acurácia global: {acc:.4f}")


novo_jogo = {
    'HomeTeamEnc': 16,
    'AwayTeamEnc': 24,
    #'TotalHomeMatches': ,
    #'TotalAwayMatches': ,
    'TotalHomeGoals': 54,
    'TotalAwayGoals': 70,
    'TotalHomeConceded': 52,
    'TotalAwayConceded': 44,
    #'AverageHomeGoalsScored': ,
    #'AverageAwayGoalsScored': ,
    #'AverageHomeGoalsConceded': ,
    #'AverageAwayGoalsConceded': ,
    #'AverageHomePoints': ,
    #'AverageAwayPoints': ,
    'TotalHomePoints': 54,
    'TotalAwayPoints': 68,
    #'AverageHomeGoalsScoredLast6': ,
    #'AverageAwayGoalsScoredLast6': ,
    #'AverageHomeGoalsConcededLast6': ,
    #'AverageAwayGoalsConcededLast6': ,
    #'AverageHomePointsLast6': ,
    #'AverageAwayPointsLast6': ,
    #'IsItEliteHome': 0,
    #'IsItEliteAway': 1,
    'HistoricalAvgHomePoints': 43.47,
    'HistoricalAvgAwayPoints': 68.8
}

df_novo = pd.DataFrame([novo_jogo])
probs = model.predict_proba(df_novo)[0]  # pega o array de probabilidades

for classe, p in zip(model.classes_, probs):
    print(f"Probabilidade de {classe}: {p*100:.1f}%")
   

#"""







