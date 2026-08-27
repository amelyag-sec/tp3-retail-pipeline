# Retail Data Pipeline Challenge — TP3 Data Engineering & MLOps

Mini-chaîne Data Engineering : des fichiers CSV de transactions jusqu'à une API interrogeable, via un Data Warehouse PostgreSQL en modèle en étoile, orchestrée avec Apache Airflow et conteneurisée avec Docker.

## Architecture

CSV (sources) vers NiFi/Ingestion vers Airflow (orchestration) vers PostgreSQL (Data Warehouse) vers API FastAPI vers Docker

## Structure du dépôt

- sql/create_tables.sql : schéma PostgreSQL (modèle en étoile)
- data/clean_transactions.py : nettoyage et validation
- data/load_warehouse.py : chargement dans PostgreSQL
- data/reference/ : stores.csv, products.csv, customers.csv (non versionnés)
- data/transactions/ : fichiers de ventes journaliers (non versionnés)
- dags/retail_pipeline_dag.py : DAG Airflow (ingest -> validate -> transform -> load)
- api/main.py, Dockerfile, requirements.txt : API FastAPI conteneurisée
- docker-compose.yml : PostgreSQL + API
- docker-compose.yaml : stack Airflow (fichier officiel Apache)

## Prérequis

- Docker Desktop (avec intégration WSL2 si Windows)
- Python 3.10+
- Git

## Installation

git clone git@github.com:amelyag-sec/tp3-retail-pipeline.git
cd tp3-retail-pipeline
python3 -m venv venv
source venv/bin/activate
pip install pandas psycopg2-binary fastapi uvicorn

Placer les données fournies dans data/reference/ (stores.csv, products.csv, customers.csv) et data/transactions/ (fichiers sales_*.csv).

## Exécution

### 1. PostgreSQL et API (Docker)

docker compose up -d --build

Crée automatiquement les 5 tables et démarre l'API sur http://localhost:8000/docs

### 2. Airflow (stack officielle)

mkdir -p logs plugins config
echo -e "AIRFLOW_UID=$(id -u)" > .env
docker compose -f docker-compose.yaml up airflow-init
docker compose -f docker-compose.yaml up -d

Interface : http://localhost:8080 (identifiants airflow / airflow)

### 3. Déclencher le pipeline

Dans l'interface Airflow, activer puis déclencher le DAG retail_pipeline. Il enchaîne : ingest_data, validate_and_transform, load_warehouse_task.

### 4. Interroger l'API

GET /sales/summary
GET /sales/by-store
GET /sales/by-product

## Ajouter un nouveau fichier de transactions

Déposer le fichier dans data/transactions/ puis redéclencher le DAG retail_pipeline — aucune modification de code nécessaire.

## Architecture cible (passage à l'échelle)

- Apache NiFi : ingestion des flux en continu
- Airflow : orchestration, inchangée dans son rôle
- Kubernetes : plusieurs pods de l'API pour la répartition de charge
- Prometheus / Grafana : supervision en temps réel
- CI/CD : tests et déploiements automatisés
