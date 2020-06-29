from datetime import datetime, timedelta

import airflow
import pandas as pd
import json
from airflow import DAG
from airflow.operators.bash_operator import BashOperator

with open("config.json") as json_data_file:
    config = json.load(json_data_file)

default_args = {
        'owner': 'airflow'
        }

dag = DAG(dag_id='job_postings', default_args=default_args, schedule_interval='0 18 * * *', start_date=datetime(2020,6,29))

previous = None
# create task for every search in settings
for i, (keywords, location) in enumerate(zip(config['keywords'], config['location'])):

   vpn = BashOperator(
      task_id=f'vpn_{i}',
      bash_command='nordvpn connect',
      dag=dag
   )

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

   if previous:
      previous >> vpn
   
   vpn >> scrape >> enrich >> mail
   previous = mail
