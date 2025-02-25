import json
import psycopg2
import boto3

# Configurations
MINIO_ENDPOINT = "http://localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
BUCKET_NAME = "etl-raw-data"
FILE_NAME = "crypto_data.json"

POSTGRES_HOST = "localhost"
POSTGRES_DB = "airflow"
POSTGRES_USER = "airflow"
POSTGRES_PASSWORD = "airflow"

def load_to_postgres():
    """
    About: This function retrieves the JSON data from MinIO and inserts it into PostgreSQL.
    """
    try:
        # Connect to MinIO and download the JSON file
        s3 = boto3.client(
            "s3",
            endpoint_url=MINIO_ENDPOINT,
            aws_access_key_id=MINIO_ACCESS_KEY,
            aws_secret_access_key=MINIO_SECRET_KEY
        )

        s3.download_file(BUCKET_NAME, FILE_NAME, "crypto_data.json")

        # Read JSON data
        with open("crypto_data.json", "r") as f:
            data = json.load(f)

        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD
        )
        cur = conn.cursor()

        # Insert data into the PostgreSQL table
        for currency, values in data.items():
            price = values["usd"]
            cur.execute(
                "INSERT INTO crypto_prices (currency, price_usd) VALUES (%s, %s)",
                (currency, price)
            )

        conn.commit()
        cur.close()
        conn.close()
        print("✅ Data successfully loaded into PostgreSQL.")

    except Exception as e:
        print(f"❌ Error: {e}")

# Run the function for debugging
if __name__ == "__main__":
    load_to_postgres()

