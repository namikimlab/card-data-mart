from airflow import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 0,
}

with DAG(
    dag_id="full_etl_dag",
    default_args=default_args,
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["retail", "full_etl"],
) as dag:

    trigger_ingestion = TriggerDagRunOperator(
        task_id="trigger_ingestion_dag",
        trigger_dag_id="ingestion_dag"
    )

    trigger_dbt_pipeline = TriggerDagRunOperator(
        task_id="trigger_dbt_pipeline_dag",
        trigger_dag_id="dbt_pipeline_dag"
    )

    trigger_ingestion >> trigger_dbt_pipeline
