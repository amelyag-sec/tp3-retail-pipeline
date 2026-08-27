import sys
import os
from datetime import datetime

from airflow.decorators import dag, task

# Permet d'importer les scripts du dossier data/ depuis le DAG
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "data"))

from clean_transactions import load_reference_data, load_all_transactions, clean_transactions
from load_warehouse import get_connection, load_dimensions, load_dim_date, load_fact_sales


@dag(
    dag_id="retail_pipeline",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["tp3"],
)
def retail_pipeline():

    @task
    def ingest_data():
        stores, products, customers = load_reference_data()
        raw = load_all_transactions()
        return {"n_raw": len(raw)}

    @task
    def validate_and_transform():
        stores, products, customers = load_reference_data()
        raw = load_all_transactions()
        clean, report = clean_transactions(raw, stores, products, customers)
        print("Rapport de nettoyage :", report)
        # On sauvegarde temporairement le résultat propre pour la tâche suivante
        clean.to_csv("/tmp/clean_transactions.csv", index=False)
        return report

    @task
    def load_warehouse_task():
        import pandas as pd
        stores, products, customers = load_reference_data()
        clean = pd.read_csv("/tmp/clean_transactions.csv", parse_dates=["transaction_date"])

        os.environ["POSTGRES_HOST"] = "host.docker.internal"
        conn = get_connection()
        load_dimensions(conn, stores, products, customers)
        load_dim_date(conn, clean)
        load_fact_sales(conn, clean)
        conn.close()
        return {"n_loaded": len(clean)}

    ingest_data() >> validate_and_transform() >> load_warehouse_task()


retail_pipeline()