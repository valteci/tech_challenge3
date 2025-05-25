from MLpipeline.downloader import Downloader
from MLpipeline.cleaner import clean_all
from MLpipeline.preprocessing import Preprocessing
from MLpipeline.model import Model

class Pipeline():

    def __init__(self):
        self._model: Model = None


    def download_raw_dataset(self)-> None:
        downloader = Downloader()
        downloader._baixar_england()


    def schedule_raw_data_update(self) -> None:
        downloader = Downloader()
        downloader._atualizar_england()


    def clear_data(self) -> None:
        clean_all()


    def load_model(self) -> None:
        pass


    def get_model_stats(self) -> None:
        pass


    def predict(self) -> None:
        pass