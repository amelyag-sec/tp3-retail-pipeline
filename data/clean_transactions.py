import glob
import pandas as pd


def load_reference_data():
    """Charge les référentiels (magasins, produits, clients) utilisés pour valider les transactions."""
    stores = pd.read_csv("data/reference/stores.csv")
    products = pd.read_csv("data/reference/products.csv")
    customers = pd.read_csv("data/reference/customers.csv")
    return stores, products, customers


def load_all_transactions():
    """Lit dynamiquement TOUS les fichiers du dossier transactions/, sans nom codé en dur."""
    files = sorted(glob.glob("data/transactions/*.csv"))
    if not files:
        raise FileNotFoundError("Aucun fichier trouvé dans data/transactions/")
    dfs = [pd.read_csv(f) for f in files]
    return pd.concat(dfs, ignore_index=True)


def clean_transactions(df, stores, products, customers):
    """Nettoie et valide le DataFrame de transactions brutes."""
    initial_count = len(df)
    report = {}

    df = df.drop_duplicates(subset=["transaction_id"])
    report["doublons_supprimes"] = initial_count - len(df)

    essential_cols = ["transaction_id", "store_id", "customer_id",
                       "product_id", "quantity", "unit_price", "transaction_date"]
    before = len(df)
    df = df.dropna(subset=essential_cols)
    report["lignes_incompletes_supprimees"] = before - len(df)

    before = len(df)
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    df = df.dropna(subset=["transaction_date"])
    report["dates_invalides_supprimees"] = before - len(df)

    before = len(df)
    df = df[df["product_id"].isin(products["product_id"])]
    df = df[df["store_id"].isin(stores["store_id"])]
    df = df[df["customer_id"].isin(customers["customer_id"])]
    report["references_inconnues_rejetees"] = before - len(df)

    df["total_amount"] = df["quantity"] * df["unit_price"]

    report["lignes_finales_propres"] = len(df)
    return df, report


if __name__ == "__main__":
    stores, products, customers = load_reference_data()
    raw = load_all_transactions()
    print(f"Transactions brutes chargées : {len(raw)}")

    clean, report = clean_transactions(raw, stores, products, customers)

    print("\n--- Rapport de nettoyage ---")
    for key, value in report.items():
        print(f"{key} : {value}")

    print("\nAperçu des données propres :")
    print(clean.head())