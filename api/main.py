import os
import psycopg2
from fastapi import FastAPI

app = FastAPI(title="Retail Data Pipeline API")


def get_connection():
    host = os.environ.get("POSTGRES_HOST", "localhost")
    return psycopg2.connect(host=host, dbname="retail_dw", user="postgres", password="postgres")


@app.get("/sales/summary")
def sales_summary():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*), SUM(total_amount) FROM fact_sales;")
    transactions, total_sales = cur.fetchone()

    cur.execute("""
        SELECT p.product_name
        FROM fact_sales f
        JOIN dim_product p ON f.product_id = p.product_id
        GROUP BY p.product_name
        ORDER BY SUM(f.total_amount) DESC
        LIMIT 1;
    """)
    best_selling_product = cur.fetchone()[0]
    conn.close()

    return {
        "total_sales": float(total_sales),
        "transactions": transactions,
        "best_selling_product": best_selling_product,
    }


@app.get("/sales/by-store")
def sales_by_store():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.store_name, SUM(f.total_amount) AS total
        FROM fact_sales f
        JOIN dim_store s ON f.store_id = s.store_id
        GROUP BY s.store_name
        ORDER BY total DESC;
    """)
    rows = cur.fetchall()
    conn.close()
    return [{"store": r[0], "total_sales": float(r[1])} for r in rows]


@app.get("/sales/by-product")
def sales_by_product():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.product_name, SUM(f.total_amount) AS total
        FROM fact_sales f
        JOIN dim_product p ON f.product_id = p.product_id
        GROUP BY p.product_name
        ORDER BY total DESC;
    """)
    rows = cur.fetchall()
    conn.close()
    return [{"product": r[0], "total_sales": float(r[1])} for r in rows]