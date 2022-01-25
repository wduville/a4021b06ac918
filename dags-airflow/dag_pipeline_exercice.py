from datetime import timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
}


dag = DAG(
    'pipeline_exercice',
    default_args=default_args,
    description='Export a release of all 9 main processes',
    schedule_interval='0 17 * * 3',
)

dag.doc_md = """
#### Dag summary
This is not a first attempt to run a DaG
#### Point of contact
wduville, medicatio
"""

start = DummyOperator(task_id='start', dag=dag)
start.__doc__ = "Stat Operator"


from src.fetch_all_datasets import fetch_all_datasets
fetch_all = PythonOperator(
    task_id='fetch_all_datasets',
    python_callable=fetch_all_datasets,
    dag=dag,
)

from src.merge_and_filter_datasets import merge_and_filter_datasets
merge_and_filter = PythonOperator(
    task_id='merge_and_filter_datasets',
    python_callable=merge_and_filter_datasets,
    dag=dag,
)

from src.export_to_csv import export_to_csv
export_to_csvs = PythonOperator(
    task_id='export_to_csv',
    python_callable=export_to_csv,
    dag=dag,
)

from src.fetch_all_organizations import fetch_all_push_mongo
filter_and_push_mongo = PythonOperator(
    task_id='filter_and_push_mongo',
    python_callable=fetch_all_push_mongo,
    dag=dag,
)

start >> fetch_all >> merge_and_filter >> export_to_csvs >> filter_and_push_mongo
