from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import boto3
from dotenv import load_dotenv

load_dotenv(dotenv_path="/opt/airflow/dags/.env")

# Load environment variables
S3_BUCKET = os.getenv("S3_BUCKET")
S3_KEY = os.getenv("S3_KEY")
LOCAL_FILE_PATH = os.getenv("LOCAL_FILE_PATH")

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# Function to download the Excel file from S3
def download_from_s3():
    os.makedirs(os.path.dirname(LOCAL_FILE_PATH), exist_ok=True)  # <-- create dirs

    print("📦 S3_BUCKET:", S3_BUCKET)
    print("🗂 S3_KEY:", S3_KEY)
    print("📍 LOCAL_FILE_PATH:", LOCAL_FILE_PATH)

    if not all([S3_BUCKET, S3_KEY, LOCAL_FILE_PATH]):
        raise ValueError("❌ One or more environment variables are missing or invalid")

    s3 = boto3.client("s3")
    s3.download_file(S3_BUCKET, S3_KEY, LOCAL_FILE_PATH)
    print(f"✅ Downloaded {S3_KEY} from S3 to {LOCAL_FILE_PATH}")

with DAG(
    dag_id="transaction_dag",
    default_args=default_args,
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,  # Manual trigger for now
    catchup=False,
    tags=["retail", "dbt"],
) as dag:

    # Task 1: Download raw data from S3
    download_data = PythonOperator(
        task_id="download_data",
        python_callable=download_from_s3
    )

    # Task 2: Load data into PostgreSQL using your existing Python script
    load_to_postgres = BashOperator(
        task_id="load_to_postgres",
        bash_command="python /opt/airflow/scripts/prepare_data.py"
    )

    # Task 3: Run dbt transformations
    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/airflow/dbt && dbt run --profiles-dir /opt/airflow/dbt"
    )

    # Task 4: Run dbt tests
    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="cd /opt/airflow/dbt && dbt test --profiles-dir /opt/airflow/dbt"
    )

    download_data >> load_to_postgres >> dbt_run >> dbt_test
