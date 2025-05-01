from datetime import datetime


BASE_URL_ELITE = "https://www.football-data.co.uk/mmz4281"
BASE_URL = "https://www.football-data.co.uk/new"

# main leagues ==========================
ENGLAND_LEAGUES = ['E0', 'E1', 'E2', 'E3']
GERMANY_LEAGUES = ['D1', 'D2']
SPAIN_LEAGUES = ['SP1', 'SP2']
ITALY_LEAGUES = ['I1', 'I2']
FRANCE_LEAGUES = ['F1', 'F2']
SCOTLAND_LEAGUES = ['SC0', 'SC1', 'SC2', 'SC3']
NETHERLANDS_LEAGUES = ['N1']
BELGIUM_LEAGUES = ['B1']
PORTUGAL_LEAGUES = ['P1']
TURKEY_LEAGUES = ['T1']
GREECE_LEAGUES = ['G1']
# =======================================



# other leagues ==========================
ARGENTINA_LEAGUE = 'ARG'
AUSTRIA_LEAGUE = 'AUT'
BRASIL_LEAGUE = 'BRA'
CHINA_LEAGUES = 'CHN'
DINAMARCA_LEAGUES = 'DNK'
FINLANDIA_LEAGUES = 'FIN'
IRLANDA_LEAGUES = 'IRL'
JAPAO_LEAGUES = 'JPN'
MEXICO_LEAGUES = 'MEX'
NORUEGA_LEAGUES = 'NOR'
POLONIA_LEAGUES = 'POL'
ROMENIA_LEAGUES = 'ROU'
RUSSIA_LEAGUES = 'RUS'
SUECIA_LEAGUES = 'SWE'
SUICIA_LEAGUES = 'SWZ'
EUA_LEAGUES = 'USA'

# ========================================


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}


class Season:
    def __init__(self, inicial: int, final: int):
        self._inicial: int = inicial
        self._final: int = final


    def next(self) -> bool:
        ano_atual = datetime.strftime(datetime.now(), "%Y")[-2:]

        if self._final == int(ano_atual):
            return False
        
        if self._inicial == 99:
            self._inicial = 0
            self._final += 1
            return True

        if self._final == 99:
            self._inicial += 1
            self._final = 0
            return True
        
        self._inicial += 1
        self._final += 1

        return True
    
    @property
    def date(self) -> str:
        data_inicial = ''
        data_final = ''

        if self._inicial >= 0 and self._inicial <= 9:
            data_inicial = '0' + str(self._inicial)
        else:
            data_inicial = str(self._inicial)
        
        if self._final >= 0 and self._final <= 9:
            data_final = '0' + str(self._final)
        else:
            data_final = str(self._final)

        return data_inicial + data_final
