import requests
from datetime import datetime, timedelta

API_URL = "http://final-project.simulative.ru/data"

# Проверяем разные даты
test_dates = ['2023-01-01', '2022-01-01', '2021-01-01']

for el in test_dates:
    url = f'{API_URL}?date={el}'
    try:
        res = requests.get(url)
        data = res.json()
        print(f"{el}: {len(data)} записей")
    except Exception as e:
        print(f"Ошибка: {e}, {res.text}")
        continue

# За дату '2021-01-01' нет данных

test_dates = ['2021-01-01', '2021-06-01', '2021-09-01', '2021-12-31' ]

for el in test_dates:
    url = f'{API_URL}?date={el}'
    try:
        res = requests.get(url)
        data = res.json()
        print(f"{el}: {len(data)} записей")
    except Exception as e:
        print(f"Ошибка: {e}, {res.text}")
        continue