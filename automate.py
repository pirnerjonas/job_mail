from datetime import datetime, timedelta

import airflow
import pandas as pd
import json
from airflow import DAG
from airflow.operators.bash_operator import BashOperator

with open("config.json") as json_data_file:
    config = json.load(json_data_file)

default_args = {
        'owner': 'airflow',
        'start_date': datetime.today() - timedelta(days=1)
        }

dag = DAG(dag_id='job_postings', default_args=default_args, schedule_interval='@daily')

# create task for every search in settings
for i, (keywords, location) in enumerate(zip(config['keywords'], config['location'])):

   scrape = BashOperator(
      task_id=f'crawl_{i}',
      bash_command= """ cd ~/Documents/job_mail/scraping/ && scrapy crawl linkedin -a keywords="{{params.keywords}}" -a location="{{params.location}}" -a filter_time="1" """,
      dag=dag,
      params={'keywords':keywords, 'location':location}
   )

   enrich = BashOperator(
      task_id=f'enrich_{i}',
      bash_command='cd ~/Documents/job_mail/ && python main.py',
      dag=dag
   )

   mail = BashOperator(
      task_id=f'mail_{i}',
      bash_command= """cd ~/Documents/job_mail/flask_mail && python mail_app.py --keywords "{{params.keywords}}" --location "{{params.location}}" --username "{{params.username}}" --password "{{params.password}}" --recipient "{{params.recipient}}" """,
      dag=dag,
      params={'keywords':keywords, 'location':location, 'username':config['gmail_username'], 'password':config['gmail_password'], 'recipient':config['recipient']}
   )

   scrape >> enrich >> mail
