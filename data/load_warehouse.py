import os
import psycopg2
from psycopg2.extras import execute_values
import pandas as pd
from clean_transactions import load_reference_data, load_all_transactions, clean_transactions


def get_connection():
    host = os.environ.get("POSTGRES_HOST", "localhost")
    return psycopg2.connect(host=host, dbname="retail_dw", user="postgres", password="postgres")

def load_dimensions(conn, stores, products, customers):
    with conn.cursor() as cur:
        execute_values(cur,
            "INSERT INTO dim_store (store_id, store_name, city, country) VALUES %s ON CONFLICT (store_id) DO NOTHING",
            stores[["store_id", "store_name", "city", "country"]].values.tolist())
        execute_values(cur,
            "INSERT INTO dim_product (product_id, product_name, category, catalog_unit_price) VALUES %s ON CONFLICT (product_id) DO NOTHING",
            products[["product_id", "product_name", "category", "unit_price"]].values.tolist())
        execute_values(cur,
            "INSERT INTO dim_customer (customer_id, customer_name, city, customer_type) VALUES %s ON CONFLICT (customer_id) DO NOTHING",
            customers[["customer_id", "customer_name", "city", "customer_type"]].values.tolist())
    conn.commit()


def load_dim_date(conn, clean_df):
    dates = pd.DataFrame({"full_date": clean_df["transaction_date"].dt.date.unique()})
    dates["year"] = pd.to_datetime(dates["full_date"]).dt.year
    dates["month"] = pd.to_datetime(dates["full_date"]).dt.month
    dates["day"] = pd.to_datetime(dates["full_date"]).dt.day
    dates["weekday"] = pd.to_datetime(dates["full_date"]).dt.day_name().str[:3]
    with conn.cursor() as cur:
        execute_values(cur,
            "INSERT INTO dim_date (full_date, year, month, day, weekday) VALUES %s ON CONFLICT (full_date) DO NOTHING",
            dates.values.tolist())
    conn.commit()


def load_fact_sales(conn, clean_df):
    df = clean_df.copy()
    df["sale_date"] = df["transaction_date"].dt.date
    rows = df[["transaction_id", "store_id", "customer_id", "product_id",
               "sale_date", "quantity", "unit_price", "total_amount"]].values.tolist()
    with conn.cursor() as cur:
        execute_values(cur,
            "INSERT INTO fact_sales (transaction_id, store_id, customer_id, product_id, sale_date, quantity, unit_price, total_amount) VALUES %s ON CONFLICT (transaction_id) DO NOTHING",
            rows)
    conn.commit()


if __name__ == "__main__":
    stores, products, customers = load_reference_data()
    raw = load_all_transactions()
    clean, report = clean_transactions(raw, stores, products, customers)

    conn = get_connection()
    load_dimensions(conn, stores, products, customers)
    load_dim_date(conn, clean)
    load_fact_sales(conn, clean)
    conn.close()

    print(f"{len(clean)} transactions chargées dans PostgreSQL.")