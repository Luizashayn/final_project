import requests
from datetime import datetime, timedelta

API_URL = "http://final-project.simulative.ru/data"

<<<<<<< HEAD
#Проверяем разные даты
=======
# Проверяем разные даты
>>>>>>> cfe4d50a427f1e6eab3e64cde5bb1f3cc8b2633b
test_dates = ['2023-01-01', '2022-01-01', '2021-01-01', '2021-12-31']

for el in test_dates:
    url = f'{API_URL}?date={el}'
    try:
        res = requests.get(url)
        data = res.json()
        print(f"{el}: {len(data)} записей")
    except Exception as e:
        print(f"Ошибка: {e}, {res.text}")
        continue

<<<<<<< HEAD
# Данные доступны с '2022-01-01'
=======
# Данные достуаны с '2022-01-01'
>>>>>>> cfe4d50a427f1e6eab3e64cde5bb1f3cc8b2633b
