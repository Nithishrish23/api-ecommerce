import sys
import os
import psycopg2
import random

# Ensure project root (API_ecommerce) is on sys.path so `config.settings` can be imported
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.settings import Config
DB_PARAMS = {
    'database': Config.DB_NAME,
    'user': Config.DB_USER,
    'password': Config.DB_PASSWORD,
    'host': Config.DB_HOST,
    'port': Config.DB_PORT,
}


def get_conn():
    return psycopg2.connect(**DB_PARAMS)


def ensure_demo_seller(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM seller_users WHERE email=%s LIMIT 1;", ('test@gmail.com',))
        seller_id = cur.fetchone()[0]
        conn.commit()
        print('Created demo seller with id', seller_id)
        return seller_id


def seed_products(conn, seller_id, count=20):
    inserted = []
    with conn.cursor() as cur:
        for i in range(count):
            name = f"Demo Product {i+1}"
            category = ['electronics','clothing','food'][i % 3]
            sub = ['phones','laptops','accessories'][i % 3]
            product_type = ['Gadget','Apparel','Grocery'][i % 3]
            unit_price = round(random.uniform(10,200),2)
            stock = random.randint(1,100)
            thumbnail = './uploads/thumbnail/plc.png'
            cur.execute("""
                INSERT INTO add_product (
                    userid, product_name, product_description, product_category, sub_category,
                    sub_sub_category, product_type, product_sku, unit, unit_price, current_stock_qty,
                    product_thumbnail
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING pid;
            """,
            (seller_id, name, name + ' description', category, sub, '', product_type, f'SKU{i+1}', 'pcs', unit_price, stock, thumbnail)
            )
            pid = cur.fetchone()[0]
            inserted.append(pid)
        conn.commit()
    print(f"Inserted {len(inserted)} demo products. PIDs: {inserted}")


if __name__ == '__main__':
    try:
        conn = get_conn()
    except Exception as e:
        print('DB connection failed:', e)
        raise
    try:
        sid = ensure_demo_seller(conn)
        seed_products(conn, sid, 20)
    finally:
        conn.close()
