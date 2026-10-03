import textwrap
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

with DAG(
	'autoru_scraper',
	default_args = {
		"depends_on_past": False,
		"retries": 1,
		"retry_delay": timedelta(minutes=5),
	},
	description="AutoRuScraper: парсинг объявлений из auto.ru  запись в БД",
	schedule=timedelta(days=14),
	start_date=datetime(2026, 10, 1),
	catchup=False,
	tags=["scraper"],
	
) as dag:
	
	t1 = BashOperator(
        task_id="scrape",
        bash_command="/home/artur/Документы/Airflow/dags/projects/AutoRuScraper/venv/bin/python "
                     "/home/artur/Документы/Airflow/dags/projects/AutoRuScraper/main.py",
    )
    
	t1.doc_md = textwrap.dedent(
		"""
		Запуск скрапера и сохранение в БД
		"""
	)