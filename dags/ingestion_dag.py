import os
import boto3
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="/opt/airflow/.env")

# Load variables from .env
USE_LOCAL_FILE = os.getenv("USE_LOCAL_FILE", "True").lower() == "true"
S3_BUCKET = os.getenv("S3_BUCKET")
S3_KEY = os.getenv("S3_KEY")
LOCAL_FILE_PATH = os.getenv("LOCAL_FILE_PATH")

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def prepare_file():
    """
    Either use local file or download from S3 based on USE_LOCAL_FILE flag
    """
    if USE_LOCAL_FILE:
        print(f"✅ Using local file: {LOCAL_FILE_PATH}")
        if not os.path.exists(LOCAL_FILE_PATH):
            raise FileNotFoundError(f"❌ Local file not found: {LOCAL_FILE_PATH}")
    else:
        print("📦 Downloading from S3...")
        os.makedirs(os.path.dirname(LOCAL_FILE_PATH), exist_ok=True)
        s3 = boto3.client("s3")
        s3.download_file(S3_BUCKET, S3_KEY, LOCAL_FILE_PATH)
        print(f"✅ Downloaded {S3_KEY} to {LOCAL_FILE_PATH}")


with DAG(
    dag_id="ingestion_dag",
    default_args=default_args,
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["retail", "ingestion"],
) as dag:

    prepare_file_task = PythonOperator(
        task_id="prepare_file",
        python_callable=prepare_file
    )

    load_to_postgres_task = BashOperator(
        task_id="load_to_postgres",
        bash_command="python /opt/airflow/scripts/prepare_data.py"
    )

    prepare_file_task >> load_to_postgres_task
