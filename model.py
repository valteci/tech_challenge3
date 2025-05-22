from preprocessing import Preprocessing
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler  # ou MinMaxScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, accuracy_score
from lightgbm import LGBMClassifier, early_stopping, log_evaluation
from sklearn.metrics import classification_report, accuracy_score


# 1. Exporta os dados
preprocessing = Preprocessing()
preprocessing.export_data()
data = preprocessing.export

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







