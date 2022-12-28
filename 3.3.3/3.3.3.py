import pandas as pd
import requests

class GetterVacanciesHH:
    """Класс обаботки данных полученных с hh
     Atributes: dict_vacancies (dict) : словарь с данными  для dataFrame
    """
    def __init__(self):
        """Иництализирует класс GetterVacanciesHH"""
        self.dict_vacancies = {"name": [], "salary_from": [],
                               "salary_to": [],"salary_currency": [],
                               "area_name": [], "published_at": []}

    #выдает путь по которому нужно сделать запрос
    get_url = lambda self,date_from, date_to, page :  f'https://api.hh.ru/vacancies?date_from={date_from}' \
                                                 f'&date_to={date_to}&specialization=1&per_page=100&page={page}'

    def get_vacancies(self):
        """Создает csv файл с вакансиями полученными при помощи hh api
        """
        dates = ['2022-12-26T00:00:00', '2022-12-26T12:00:00','2022-12-27T00:00:00']
        for date in dates:
            for page in range(1, 20):
                response = {}
                while True:
                    try:
                        response = requests.get(self.get_url(date, dates[2], page))
                        if response.status_code == 200:
                            response = response.json()
                            break
                    except:
                        continue
                print(page)
                for item in response["items"]:
                    self.dict_vacancies['name'].append(item["name"])
                    salary = item['salary']
                    self.dict_vacancies['salary_to'].append(None if salary is None else salary["to"])
                    self.dict_vacancies['salary_from'].append(None if salary is None else salary["from"])
                    self.dict_vacancies['salary_currency'].append(None if salary is None else salary["currency"])
                    area = item['area']
                    self.dict_vacancies['area_name'].append(None if area is None else area["name"])
                    self.dict_vacancies['published_at'].append(item['published_at'])
        df = pd.DataFrame(self.dict_vacancies)
        df.to_csv('hh_response.csv')
GetterVacanciesHH().get_vacancies()