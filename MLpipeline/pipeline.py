from MLpipeline.downloader import Downloader
from MLpipeline.cleaner import clean_all
from MLpipeline.preprocessing import Preprocessing
from MLpipeline.model import Model

class Pipeline():

    def __init__(self):
        self._model: Model = None
        self._model_stats: dict = None


    def download_raw_dataset(self)-> None:
        downloader = Downloader()
        downloader._baixar_england()


    def raw_data_update(self) -> None:
        downloader = Downloader()
        downloader._atualizar_england()


    def clear_data(self) -> None:
        clean_all()


    def load_model(self) -> None:
        # modelos: logistic_regression, xgboost, lightgbm
        self._model = Model('xgboost')
        self._model.training()


    def print_model_stats(self) -> None:
        self._model.print_model_stats()


    def predict(self, home_team: str, away_team: str) -> dict:
        return self._model.predict(home_team, away_team)