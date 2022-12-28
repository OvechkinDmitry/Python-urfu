import pandas as pd
import numpy as np
from apiTask import CurrencyReflector


class SalaryConverter:
    """
    Класс для конвертации валют в рубли
    Attributes:
        csv_currencies (DataFrame): csv-файл с коэффициентами
        currencies (dict): все доступные валюты
        csv_file (DataFrame): все данные из csv-файла
        data (dict): данные для формирования итогового отформатированного csv-файла
    """
    def __init__(self,file_name):
        """Инициализирует класс Converter
        Args:
            file_name (string): название csv_file для дальнейшего редактирования
        """
        self.csv_currencies = pd.read_csv("currencies.csv")
        self.vac_data = CurrencyReflector(file_name)
        self.currencies = self.vac_data.currencies_by_months
        self.csv_file = self.vac_data.csv_data

    def get_converted_csv(self):
        """ Формирует csv файл с вакансиями и их зарплатами сконвертированными в рубли
        """
        frame_data = {"name": [], "salary": [], "area_name": [], "published_at": []}
        for index, row in self.csv_file.iterrows():
            salary_from, salary_to, value_curr = row["salary_from"], row["salary_to"], row["salary_currency"]
            print(type(salary_to))
            if len(frame_data['name']) >= 100:
                break
            if not np.isnan(salary_from) or not np.isnan(salary_to) and value_curr in self.currencies:
                coefficient = float(
                        *self.csv_currencies[self.csv_currencies["date"] == row["published_at"][:7]][value_curr].values)\
                            if value_curr != 'RUR' else 1
                frame_data["salary"].append(salary_from * coefficient) if np.isnan(salary_to) else\
                frame_data["salary"].append(salary_to * coefficient) if np.isnan(salary_from) else\
                frame_data["salary"].append(((salary_from + salary_to) / 2) * coefficient)
                for field in ["name", "area_name", "published_at"]:
                   frame_data[field].append(row[field])
        result_csv_file = pd.DataFrame(frame_data).head(100)
        result_csv_file.to_csv("3.3.2.csv")


SalaryConverter("../vacancies_dif_currencies.csv").get_converted_csv()
