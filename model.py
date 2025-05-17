import pandas as pd
from utils import Season

class Model:

    DATA_PATH = './cleaned_data'

    def __init__(self):
        self._datas: list[pd.DataFrame] = []

    def _load_data(self) -> None:
        season = Season(19, 20)

        while season.next():
            file_name = f'{Model.DATA_PATH}/{season.date}.csv'
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



model = Model()
model._load_data()
print(model.datas[0].describe())
