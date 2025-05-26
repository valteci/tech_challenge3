from MLpipeline.preprocessing import Preprocessing, Search
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler  # ou MinMaxScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, accuracy_score
from lightgbm import LGBMClassifier, early_stopping, log_evaluation
from sklearn.metrics import classification_report, accuracy_score
import numpy as np
import xgboost as xgb
from xgboost.callback import EarlyStopping



class Model:
    def __init__(self, model_type: str = 'lightgbm'):
        preprocessing = Preprocessing()
        preprocessing.export_data()

        self._data = preprocessing.export
        self._encoding_table = preprocessing.encoding_table
        self._model_type = model_type
        self._model = None
        self._model_stats: dict = {}
        self._scaler = None


    def training(self) -> None:

        # 2. Separa features e target
        X = self._data.drop(
            columns=[
                'FTR',
                'FTHG',
                'FTAG',
                'TotalHomeMatches',
                'TotalAwayMatches',
                'AverageHomeGoalsScored',
                'AverageAwayGoalsScored',
                'AverageHomeGoalsConceded',
                'AverageAwayGoalsConceded',
                'AverageHomePoints',
                'AverageAwayPoints',
                'AverageHomeGoalsScoredLast6',
                'AverageAwayGoalsScoredLast6',
                'AverageHomeGoalsConcededLast6',
                'AverageAwayGoalsConcededLast6',
                'AverageHomePointsLast6',
                'AverageAwayPointsLast6',
                #'IsItEliteHome',
                #'IsItEliteAway',
                'HomeTeamEnc',
                'AwayTeamEnc',
                'HistoricalAvgHomePoints',
                'HistoricalAvgAwayPoints',
            ]
        )

        y = self._data['FTR'].astype(str)

        # 3. Split treino/teste estratificado
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=0.2,
            stratify=y,
            random_state=42
        )


        if self._model_type == 'lightgbm':
            self._training_lightgbm(X_train, X_test, y_train, y_test)

        elif self._model_type == 'logistic_regression':
            self._training_logistic_regression(X_train, X_test, y_train, y_test)

        elif self._model_type == 'xgboost':
            self._training_xgboost(X_train, X_test, y_train, y_test)


    def _training_lightgbm(self, X_train, X_test, y_train, y_test) -> None:
        self._model = LGBMClassifier(
                objective='multiclass',
                num_class=3,
                boosting_type='gbdt',
                learning_rate=0.05,
                n_estimators=500,
                num_leaves=31,
                random_state=42
            )

        # 5. Treina com early stopping no conjunto de teste
        self._model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            eval_metric='multi_logloss',
            callbacks=[
                early_stopping(stopping_rounds=20),    # interrompe se não melhorar por 20 iters
                log_evaluation(period=50)],
        )

        probs = self._model.predict_proba(X_test)
        preds = self._model.predict(X_test)

        self._model_stats['Log-loss'] = log_loss(y_test, probs)
        self._model_stats['Accuracy'] = accuracy_score(y_test, preds)


    def _training_logistic_regression(
        self,
        X_train,
        X_test,
        y_train,
        y_test
    ) -> None:

        self._scaler = MinMaxScaler()            # para normalização [0–1], use MinMaxScaler()
        #scaler = StandardScaler()
        x_train_scaled = self._scaler.fit_transform(X_train)
        x_test_scaled  = self._scaler.transform(X_test)

        # 5. Criação do modelo
        self._model = LogisticRegression(
            solver='lbfgs',       # multinomial por padrão no sklearn >=1.7
            max_iter=1000,
            random_state=32463
        )

        # 6. Treinamento
        self._model.fit(x_train_scaled, y_train)

        # 7. Previsões
        probs = self._model.predict_proba(x_test_scaled)
        preds = self._model.predict(x_test_scaled)

        # 8. Avaliação
        self._model_stats['Log-loss'] = log_loss(y_test, probs)
        self._model_stats['Accuracy'] = accuracy_score(y_test, preds)


    def _training_xgboost(self, X_train, X_test, y_train, y_test) -> None:
        # 0. Criar mapeamento classes→int e int→classes
        # (aqui usamos tanto train quanto test caso seja preciso)
        unique_labels = sorted(pd.concat([y_train, y_test]).unique())
        self._class_to_int = {lbl: idx for idx, lbl in enumerate(unique_labels)}
        self._int_to_class = {idx: lbl for lbl, idx in self._class_to_int.items()}

        # 1. Converte y para inteiros
        y_train_int = y_train.map(self._class_to_int)
        y_test_int  = y_test.map(self._class_to_int)

        # 2. Converte para DMatrix
        dtrain = xgb.DMatrix(X_train, label=y_train_int.values)
        dtest  = xgb.DMatrix(X_test,  label=y_test_int.values)

        # 3. Parâmetros
        params = {
            'objective':   'multi:softprob',
            'num_class':   len(self._class_to_int),
            'learning_rate': 0.05,
            'max_depth':   6,
            'seed':        42,
            'eval_metric': 'mlogloss'
        }

        # 4. Treina com early stopping
        watchlist = [(dtest, 'validation')]
        booster = xgb.train(
            params,
            dtrain,
            num_boost_round=500,
            evals=watchlist,
            early_stopping_rounds=20,
            verbose_eval=50
        )

        # 5. Guarda o booster
        self._model = booster

        # 6. Calcula métricas numéricas
        probs = booster.predict(dtest)            # shape (n_samples, n_classes)
        preds_int = np.argmax(probs, axis=1)

        self._model_stats['Log-loss'] = log_loss(y_test_int, probs)
        self._model_stats['Accuracy'] = accuracy_score(y_test_int, preds_int)


    def predict(self, home_team: str, away_team: str) -> dict:
        stats = {
            #'HomeTeamEnc': 0,
            #'AwayTeamEnc': 0,
            'TotalHomeGoals' : 0,
            'TotalAwayGoals' : 0,
            'TotalHomeConceded' : 0,
            'TotalAwayConceded' : 0,
            'TotalHomePoints': 0,
            'TotalAwayPoints': 0,
            'IsItEliteHome': 0,
            'IsItEliteAway': 0,
            #'HistoricalAvgHomePoints': 0,
            #'HistoricalAvgAwayPoints': 0,
        }

        #stats['HomeTeamEnc'] = self._encoding_table[home_team]
        #stats['AwayTeamEnc'] = self._encoding_table[away_team]

        search = Search(self._encoding_table, self._data)

        stats['TotalHomeGoals'] = search.search_total_goals(home_team)
        stats['TotalAwayGoals'] = search.search_total_goals(away_team)
        stats['TotalHomeConceded'] = search.search_total_conceded(home_team)
        stats['TotalAwayConceded'] = search.search_total_conceded(away_team)
        stats['TotalHomePoints'] = search.search_total_points(home_team)
        stats['TotalAwayPoints'] = search.search_total_points(away_team)
        stats['IsItEliteHome'] = search.is_it_elite(home_team)
        stats['IsItEliteAway'] = search.is_it_elite(away_team)

        #stats['HistoricalAvgAwayPoints'] = 45
        #stats['HistoricalAvgHomePoints'] = 60
        print(stats)

        df_novo = pd.DataFrame([stats])

        if self._model_type == 'xgboost':
            return self._predict_xgboost(df_novo)

        if self._scaler:
            df_novo = self._scaler.transform(df_novo)

        probs = self._model.predict_proba(df_novo)[0]  # pega o array de probabilidades

        result = {}
        for classe, p in zip(self._model.classes_, probs):
            result[classe] = f'{p*100:.1f}%'

        return result



    def _predict_xgboost(self, data: pd.DataFrame) -> dict:
        dnew = xgb.DMatrix(data)
        probs = self._model.predict(dnew)[0]

        return {
            self._int_to_class[i]: f'{p*100:.1f}%'
            for i, p in enumerate(probs)
        }
    

    def _predict_logistic_regression(self, data: pd.DataFrame) -> dict:
        df_novo = self._scaler.transform(df_novo)



    def predict_custom(self, ) -> dict:
        return {}


#modelo = Model('logistic_regression')
#modelo.training()
#print(modelo.predict("Tottenham", 'Brighton'))
#print(modelo.predict("Bournemouth", 'Leicester'))
#print(modelo.predict("Fulham", 'Man City'))
#print(modelo.predict("Wolves", 'Brentford'))
#print(modelo.predict("Nott'm Forest", 'Chelsea'))
#print(modelo.predict("Man United", 'Aston Villa'))
#print(modelo.predict("Southampton", 'Arsenal'))
#print(modelo.predict("Newcastle", 'Everton'))
#print(modelo.predict("Liverpool", 'Crystal Palace'))
#print(modelo.predict("Ipswich", 'West Ham'))

#print(modelo._model_stats)

preprocessing = Preprocessing()
preprocessing.export_data()
data = preprocessing._encoding_table
string = '[\n'
for index in data:
    string += '"' + index + '"' + ', \n'

string += ']'
print(string)