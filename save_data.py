import requests
import csv
from datetime import datetime, timedelta
import os
from config import *
import pandas as pd
import sys

print("=== save_data.py запущен ===")
sys.stdout.flush()

#вычисляю вчерашнюю дату
today = datetime.now().date()
yesterday = today - timedelta(days = 1)
yesterday_str = yesterday.strftime('%Y-%m-%d')

#подставляю дату в Url
url = f'{API_URL}?date={yesterday_str}'

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
else:
    print(f"Ошибка! Статус: {response.status_code}")

# создаем папку
os.makedirs(DATA_DIR, exist_ok=True)

# Сохраняем в CSV
if data:
    filename = f"sales_{yesterday_str}.csv"
    filepath = os.path.join(DATA_DIR, filename)
    df = pd.DataFrame(data)
    
    # перевожу секунды во время суток
    seconds = df['purchase_time_as_seconds_from_midnight']
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    df['purchase_time_str'] = hours.astype(str).str.zfill(2) + ':' + minutes.astype(str).str.zfill(2) + ':' + secs.astype(str).str.zfill(2)

    df[['client_id', 'gender', 'purchase_datetime', 'purchase_time_str', 'product_id', 'quantity', 'price_per_item', 'discount_per_item', 'total_price']].to_csv(filepath, index=False, encoding='utf-8')
    print(f"Загружено {len(df)} записей")