from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
from io import StringIO
import polars as pl
import boto3
import logging
from datetime import datetime
logging.basicConfig(
     filename='log_file_name.log',
     level=logging.INFO,
     format= '[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
     datefmt='%H:%M:%S'
 )

# set up logging to console
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)

logger = logging.getLogger(__name__)

def extract(**kwargs):
    logging.info('Starting extract function')
    url = 'https://people.sc.fsu.edu/~jburkardt/data/csv/airtravel.csv'
    df = pl.read_csv(url)
    kwargs['ti'].xcom_push(key='extracted_data', value=df)
    logging.info('Extract function completed')
    logger.info(df.head(5))


def transform(**kwargs):
    logger.info('Starting transform function')
    data = kwargs['ti'].xcom_pull(key='extracted_data')
    logger.info(data.head(5))
    # Remove "" in column names
    data.columns = data.columns.str.replace('"', '')
    # Remove whitespace in column names
    data.columns = data.columns.str.strip()
    data['Total'] = data['1958'] + data['1959'] + data['1960']
    kwargs['ti'].xcom_push(key='transformed_data', value=data)
    logger.info('Transform function completed')


def load(**kwargs):
    logger.info('Starting load function')
    data = kwargs['ti'].xcom_pull(key='transformed_data')
    s3 = boto3.resource('s3')
    bucket = 'airflow-dags-sample'
    csv_buffer = StringIO()
    data.to_csv(csv_buffer)
    filename = f"data/{datetime.now().strftime('%Y-%m-%d')}.csv"
    s3.Object(bucket, filename).put(Body=csv_buffer.getvalue())
    logger.info('Load function completed, data loaded to s3')

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 10, 30),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
}


with DAG(dag_id="mwaa-dag-demo", schedule_interval=None, catchup=False, default_args=default_args) as dag:
    task_extract = PythonOperator(
        task_id='extract',
        python_callable=extract,
        provide_context=True,
        dag=dag
    )

    task_transform = PythonOperator(
        task_id='transform',
        python_callable=transform,
        provide_context=True,
        dag=dag
    )

    task_load = PythonOperator(
        task_id='load',
        python_callable=load,
        provide_context=True,
        dag=dag
    )


task_extract >> task_transform >> task_load