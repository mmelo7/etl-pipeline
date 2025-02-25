from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import json
import boto3
import psycopg2
import time

MINIO_ENDPOINT = "http://minio:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
BUCKET_NAME = "etl-raw-data"
FILE_NAME = "crypto_data.json"
API_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"

POSTGRES_HOST = "postgres"
POSTGRES_DB = "airflow"
POSTGRES_USER = "airflow"
POSTGRES_PASSWORD = "airflow"

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 2, 24),
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
}

dag = DAG(
    "etl_pipeline",
    default_args=default_args,
    description="Extract data from API, store in MinIO, and load into PostgreSQL",
    schedule_interval=timedelta(hours=1),
)

def extract_data():
    """
    About: This function extracts cryptocurrency price data from the CoinGecko API.
    The extracted data is saved as a JSON file in the temporary directory.
    Implements rate limiting by retrying with exponential backoff in case of a 429 error.
    """
    retries = 5
    wait_time = 10

    for attempt in range(retries):
        response = requests.get(API_URL)
        data = response.json()

        if "status" in data and data["status"].get("error_code") == 429:
            print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
            wait_time *= 2
            continue
        else:
            with open("/tmp/data.json", "w") as f:
                json.dump(data, f)
            print("Data successfully extracted!")
            break
    else:
        print("Failed after multiple retries due to rate limiting.")

def load_to_minio():
    """
    About: This function uploads the extracted JSON data to MinIO.
    The data is stored in the 'etl-raw-data' bucket for further processing.
    """
    s3 = boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY
    )

    with open("/tmp/data.json", "rb") as f:
        s3.upload_fileobj(f, BUCKET_NAME, FILE_NAME)

def load_to_postgres():
    """
    About: This function retrieves the JSON data from MinIO and inserts it into PostgreSQL.
    The data is extracted, transformed into a structured format, and stored in a relational database.
    """
    s3 = boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY
    )

    s3.download_file(BUCKET_NAME, FILE_NAME, "/tmp/data.json")

    with open("/tmp/data.json", "r") as f:
        data = json.load(f)

    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )
    cur = conn.cursor()

    for currency, values in data.items():
        price = values["usd"]
        cur.execute(
            "INSERT INTO crypto_prices (currency, price_usd) VALUES (%s, %s)",
            (currency, price)
        )

    conn.commit()
    cur.close()
    conn.close()

extract_task = PythonOperator(
    task_id="extract_data",
    python_callable=extract_data,
    dag=dag,
)

load_minio_task = PythonOperator(
    task_id="load_to_minio",
    python_callable=load_to_minio,
    dag=dag,
)

load_postgres_task = PythonOperator(
    task_id="load_to_postgres",
    python_callable=load_to_postgres,
    dag=dag,
)

extract_task >> load_minio_task >> load_postgres_task
