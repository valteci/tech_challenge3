from preprocessing import Preprocessing
import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, accuracy_score


preprocessing = Preprocessing()
preprocessing.export_data()
data = preprocessing.export
#data.to_csv('teste.csv', sep=',', index=False)

# separar features e target
X = data.drop(columns=['FTR'])
y = data['FTR']

# separar treino e teste
x_train, x_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)

# criação do modelo
model = LogisticRegression(
    multi_class='multinomial',
    solver='lbfgs',
    max_iter=1000,
    random_state=42
)

# treinamento do modelo
model.fit(x_train, y_train)

# Prevendo probabilidades e classes
probs = model.predict_proba(x_test)
preds = model.predict(x_test)

# Avaliar desempenho.
loss = log_loss(y_test, probs)
acc = accuracy_score(y_test, preds)

print(f"Log-loss: {loss:.4f}")
print(f"Acurácia: {acc:.4f}")


