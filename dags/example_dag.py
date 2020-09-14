import os
from datetime import datetime, timedelta
import airflow
from airflow import DAG
from jobs.example import functions
from airflow.operators.python_operator import PythonOperator
from airflow.operators.python_operator import BranchPythonOperator
from airflow.operators.dummy_operator import DummyOperator


YEARS = [2015, 2016, 2017, 2018, 2019]

default_dag_args = {
    # Setting start date as yesterday starts the DAG immediately when it is
    # detected in the Cloud Storage bucket.
    # set your start_date : airflow will run previous dags if dags #since startdate has not run
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': airflow.utils.dates.days_ago(1),
    'email': ['lucas.abbade@gscap.com.br'],
    'project_id': 'example_scipy',
    'retries': 2,
    'retry_delay': timedelta(minutes=2)
}

dag = DAG(
    dag_id='equities_dag',
    default_args=default_dag_args,
    catchup=False,
    schedule_interval=None
)

start = DummyOperator(
    task_id='start_dag',
    dag=dag
)

download_complete = DummyOperator(
    task_id='download_complete',
    dag=dag
)

for year in YEARS:
    download_file = PythonOperator(
        task_id=f'download_file_{year}',
        op_kwargs={'year': year},
        python_callable=functions.download_year,
        dag=dag
    )

    unzip_file = PythonOperator(
        task_id=f'unzip_file_{year}',
        provide_context=True,
        op_kwargs={'year': year},
        python_callable=lambda year, **context: functions.unzip(context['task_instance'].xcom_pull(task_ids=f'download_file_{year}')),
        dag=dag
    )

    delete_zip = PythonOperator(
        task_id=f'delete_zip_{year}',
        provide_context=True,
        op_kwargs={'year': year},
        python_callable=lambda year, **context: functions.delete_zip(context['task_instance'].xcom_pull(task_ids=f'download_file_{year}')),
        dag=dag
    )

    start >> download_file >> unzip_file >> delete_zip >> download_complete

process_files = PythonOperator(
    task_id='process_files',
    python_callable=lambda: functions.process([f'dags/files/{i}' for i in os.listdir('dags/files')]),
    dag=dag
)

download_complete >> process_files
