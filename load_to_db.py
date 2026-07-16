import os
import sys
import pandas as pd
import psycopg2
from psycopg2 import sql, extras
from datetime import datetime, timedelta
from config import *

print("=== load_to_db.py запущен ===")
sys.stdout.flush()

yesterday = datetime.now().date() - timedelta(days=1)
yesterday_str = yesterday.strftime('%Y-%m-%d')

filename = f"sales_{yesterday_str}.csv"      
filepath = os.path.join(DATA_DIR, filename)

<<<<<<< HEAD
# Проверяем, существует ли файл
if not os.path.exists(filepath):
    print(f"Файл {filepath} не найден!")
    sys.exit(1)
=======
if os.path.exists(filepath):
    df = pd.read_csv(filepath)
    df['purchase_datetime'] = pd.to_datetime(df['purchase_datetime'])
>>>>>>> cfe4d50a427f1e6eab3e64cde5bb1f3cc8b2633b

# Читаем CSV
df = pd.read_csv(filepath)
df['purchase_datetime'] = pd.to_datetime(df['purchase_datetime'])
print(f"Прочитано {len(df)} записей из {filename}")

# Подключение к БД
conn = psycopg2.connect(
    host=DATABASE_CREDS["HOST"],
    port=DATABASE_CREDS["PORT"],
    database=DATABASE_CREDS["DATABASE"],
    user=DATABASE_CREDS["USER"],
    password=DATABASE_CREDS["PASSWORD"]
)

with conn.cursor() as cur:
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sales_ozon (
            id SERIAL PRIMARY KEY,
            client_id INTEGER,
            gender VARCHAR(1),
            purchase_datetime DATE,
            purchase_time_str TIME,
            product_id INTEGER,
            quantity INTEGER,
            price_per_item INTEGER,
            discount_per_item INTEGER,
            total_price INTEGER,
            load_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()

records = df.to_dict('records')

insert_query = """
    INSERT INTO sales_ozon (
        client_id, gender, purchase_datetime, purchase_time_str,
        product_id, quantity, price_per_item, discount_per_item, total_price
    ) VALUES %s
"""

with conn.cursor() as cur:
    extras.execute_values(
        cur,
        insert_query,
        [(
            r['client_id'],
            r['gender'],
            r['purchase_datetime'],
            r['purchase_time_str'],
            r['product_id'],
            r['quantity'],
            r['price_per_item'],
            r['discount_per_item'],
            r['total_price']
        ) for r in records]
    )
    conn.commit()

print(f"✅ Загружено {len(records)} записей в БД")
conn.close()