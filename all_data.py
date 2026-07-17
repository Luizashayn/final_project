import os
import time
import requests
import pandas as pd
import psycopg2
from psycopg2 import extras
from datetime import datetime, timedelta
from config import *

print("Перезаливка всех данных (с purchase_datetime_full)")

# Подключение к БД
conn = psycopg2.connect(
    host=DATABASE_CREDS["HOST"],
    port=DATABASE_CREDS["PORT"],
    database=DATABASE_CREDS["DATABASE"],
    user=DATABASE_CREDS["USER"],
    password=DATABASE_CREDS["PASSWORD"]
)

start_date = '2022-01-01'
end_date = datetime.now().date() - timedelta(days=1)
end_date_str = end_date.strftime('%Y-%m-%d')

start = datetime.strptime(start_date, '%Y-%m-%d').date()
end = datetime.strptime(end_date_str, '%Y-%m-%d').date()

total_days = (end - start).days + 1
print(f"Всего дней для загрузки: {total_days}")

# Создание папки и csv файла
os.makedirs(DATA_DIR, exist_ok=True)
output_filename = f"sales_{start_date}_to_{end_date_str}.csv"
output_filepath = os.path.join(DATA_DIR, output_filename)

total_loaded = 0
current_date = start
first_chunk = True

# 1. ОЧИЩАЕМ СТАРЫЕ ДАННЫЕ (чтобы не было дублей)
with conn.cursor() as cur:
    cur.execute("TRUNCATE TABLE sales_ozon;")
    conn.commit()
    print("Старые исторические данные удалены")

while current_date <= end:
    date_str = current_date.strftime('%Y-%m-%d')
    print(f"Обработка: {date_str}")
    
    url = f'{API_URL}?date={date_str}'
    res = requests.get(url)

    if res.status_code == 200:
        data = res.json()
        
        if data:
            df = pd.DataFrame(data)

            # Преобразуем секунды во время
            sec = df['purchase_time_as_seconds_from_midnight']
            sec = pd.to_numeric(sec, errors='coerce').fillna(0).astype(int)
            hours = (sec // 3600).astype(int)
            minutes = ((sec % 3600) // 60).astype(int)
            secs = (sec % 60).astype(int)

            df['purchase_time_str'] = (
            hours.astype(str).str.zfill(2) + ':' +
            minutes.astype(str).str.zfill(2) + ':' +
            secs.astype(str).str.zfill(2)
)
            
            # 2. СОЗДАЁМ ПОЛНУЮ ДАТУ-ВРЕМЯ
            df['purchase_datetime'] = pd.to_datetime(df['purchase_datetime'])
            df['purchase_datetime_full'] = pd.to_datetime(
                df['purchase_datetime'].astype(str) + ' ' + df['purchase_time_str'],
                errors='coerce'
            )
            
            # Удаляем строки с ошибками
            df = df.dropna(subset=['purchase_datetime_full'])
            
            # Оставляю нужные колонки
            cols = [
                'client_id', 'gender', 'purchase_datetime', 'purchase_time_str',
                'product_id', 'quantity', 'price_per_item', 'discount_per_item',
                'total_price', 'purchase_datetime_full'
            ]
            existing_cols = [c for c in cols if c in df.columns]
            df = df[existing_cols]
            
            # Сохраняю в csv
            df.to_csv(output_filepath, mode='a', header=first_chunk, index=False, encoding='utf-8')
            if first_chunk and len(df) > 0:
                first_chunk = False

            # 3. ЗАГРУЖАЮ В БД
            with conn.cursor() as cur:
                records = df.to_dict('records')
                insert_query = """
                    INSERT INTO sales_ozon (
                        client_id, gender, purchase_datetime, purchase_time_str,
                        product_id, quantity, price_per_item, discount_per_item,
                        total_price, purchase_datetime_full
                    ) VALUES %s
                """
                extras.execute_values(cur, insert_query, [
                    (
                        r['client_id'], r['gender'], r['purchase_datetime'], r['purchase_time_str'],
                        r['product_id'], r['quantity'], r['price_per_item'], r['discount_per_item'],
                        r['total_price'], r['purchase_datetime_full']
                    )
                    for r in records
                ])
                conn.commit()
                
                total_loaded += len(records)
                print(f"Загружено {len(records)} записей")
        else:
            print(f"Нет данных за {date_str}")
    else:
        print(f"Ошибка API: статус {res.status_code}")
    
    time.sleep(0.5)
    current_date += timedelta(days=1)

print(f"\nВсего загружено записей: {total_loaded}")
conn.close()
print("Подключение к БД закрыто")