from datetime import datetime
import operator
from urllib.request import urlopen
from xml.etree.ElementTree import parse
import pandas as pd
from dateutil import rrule
from dateutil.rrule import rrule, MONTHLY
from pandas import read_csv

replace_dot = lambda x:  float(x.replace(",", "."))

class CurrencyReflector:
    """Класс обработки данных о валютах, читает данные о вакансиях
        Attributes:
            file_name (string) : название файла
            series (DataFrame) : лист словарей-вакансий
            span tuple(datetime, datetime): минимальное время и максимальное время
            currencies_by_months (dict) : словарь - валюта : коэффициент
            needed_cur : валюты число которых больше 5000
        """
    def __init__(self, file_name):
        """Инициализирует объект класса CurrencyReflector
                Args:
                     file_name (string) : название файла
        """
        self.file_name = file_name
        self.csv_data = read_csv(self.file_name)
        self.series = self.csv_data.to_dict(orient="records")
        self.span = self.find_min_max(self.series, "published_at")
        dictionary_freq = self.get_dict_sorted_values(self.get_currency_frequency(self.series))
        self.needed_cur = self.get_dict_to_process(dictionary_freq)
        self.currencies_by_months = {"date": [], **{key: [] for key in self.needed_cur.keys()}}
        for key, value in dictionary_freq.items():
            print(f"Для валюты {key} -> {value}")

    #возвращает словарь валют чье число больше 5000 и не "RUR"
    get_dict_to_process = lambda self, dict: {key: value for key, value in dict.items() if value > 5000 and key != "RUR"}

    # возвращает tuple диапазона дат из вакансий
    find_min_max = lambda self, dicts, field: (min([v[field] for v in dicts]), max([v[field] for v in dicts]))

    # возвращает отсортированный словарь по значениям
    get_dict_sorted_values = lambda self, dic: dict(sorted(dic.items(), key=operator.itemgetter(1), reverse=True))

    # конвертирует валюту используя номинальному и реальному значению
    get_unit_value = lambda self, value, nominal: replace_dot(value) / replace_dot(nominal)

    def get_currency_frequency(self,dictionaties):
        """Собирает частотность валют в словарь
        Args:
            dictionaties (list[dict]): массив вакансий
        Returns:
            (dict) : словарь частотностей валют
        """
        frequencies = {}
        for d in dictionaties:
            if isinstance(d['salary_currency'], str):
                if d['salary_currency'] not in frequencies:
                    frequencies[d['salary_currency']] = 1
                else:
                    frequencies[d['salary_currency']] += 1
        return frequencies


    def get_currency_history(self):
        """Считывает историю курса валют по API cbr и выводит в виде csv
        сконвертированные в рубли валюты
        """
        start_date = datetime.strptime(self.span[0], '%Y-%m-%dT%H:%M:%S%z')
        finish_date = datetime.strptime(self.span[1], '%Y-%m-%dT%H:%M:%S%z')
        for date in rrule(freq=MONTHLY, dtstart=start_date, until=finish_date):
            self.currencies_by_months['date'] += [date.strftime('%Y-%m')]
            root = parse(urlopen(f'https://www.cbr.ru/scripts/XML_daily.asp?date_req=01/{date.strftime("%m/%Y")}')).getroot()
            currencies = root.findall('Valute')
            for cur_data in currencies:
                code = cur_data.find('CharCode').text
                if code in self.currencies_by_months.keys():
                    self.currencies_by_months[code].append(self.get_unit_value(cur_data.find('Value').text,
                                                                               cur_data.find('Nominal').text))
            for key, value in self.currencies_by_months.items():
                 if len(self.currencies_by_months[key]) == len(self.currencies_by_months['date']):
                     continue
                 else:  self.currencies_by_months[key].append(None)
        result_data = pd.DataFrame(self.currencies_by_months)
        result_data.to_csv('converted_currencies.csv')

CurrencyReflector("../vacancies_dif_currencies.csv").get_currency_history()