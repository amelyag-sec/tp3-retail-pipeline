# Dataset — Retail Data Pipeline

Ce dossier contient le jeu de données du challenge F3 Data Engineering & MLOps.

## Structure

- `reference/stores.csv` : référentiel des magasins
- `reference/products.csv` : référentiel des produits
- `reference/customers.csv` : référentiel des clients
- `transactions/` : fichiers de transactions journaliers
- `instructor_only/sales_test.csv` : fichier réservé à la démonstration/évaluation finale

## Colonnes des transactions

| Colonne | Description |
|---|---|
| transaction_id | Identifiant unique de la transaction |
| store_id | Identifiant du magasin |
| customer_id | Identifiant du client |
| product_id | Identifiant du produit |
| quantity | Quantité vendue |
| unit_price | Prix unitaire en FCFA |
| transaction_date | Date et heure de la transaction |

## Anomalies introduites

Les fichiers contiennent volontairement certaines anomalies afin de tester la qualité des pipelines :

- doublons ;
- valeurs manquantes ;
- formats de dates incorrects ;
- références produit/magasin inconnues ;
- quantités négatives.

Les participants doivent définir et justifier les règles de traitement correspondantes.
