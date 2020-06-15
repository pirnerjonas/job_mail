### Job search project

## How to use this repository

- extract data with scrapy crawler
- run `main.py` to preprocess and enrich the data
- run the flask web app to display the results

### Gather data from linkedIn 

The first step of the project is to extract job offerings from linkedIn. You can run the scrapy crawl command with three parameters:
- `keywords`: the position or job title to look for (e.g. data scientist)
- `location`: the location of the job (e.g. Berlin)
- `filter_time`: the time span of the job offerings to show


The command to extract all data scientist jobs in germany would look like this (run it in the `/scraping` directory):
``` console
scrapy crawl linkedin -a keywords="data scientist" -a location="deutschland" -a filter_time="false"
```
if you wish to extract only the jobs of the last 24 hours you can use `filter_time=1`

### Preprocessing and company ratings
The script `main.py` loads the data from the database, preprocesses it and finds ratings for new companies. 

``` console
python main.py
```

### Send job offerings per mail
``` console
python mail_app.py
```

### Airflow
cp automate.py ~/airflow/dags
airflow scheduler

new terminal
airflow webserver




airflow unpause 'job_postings' && airflow trigger_dag 'job_postings' --conf '{"keywords":"data analyst", "location":"münchen"}'