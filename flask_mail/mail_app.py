from flask import Flask, render_template, url_for
from flask_mail import Mail, Message
import pandas as pd
import ast
import datetime
import argparse



# load the data
job_df = pd.read_sql_table('jobs_preprocessed_table','sqlite:///../scraping/jobs.db')
company_df = pd.read_sql_table('company_ratings','sqlite:///../scraping/jobs.db')

# join the data
job_data = pd.merge(job_df, company_df, how='left', on=['company_name','city'])

# sort dataframe 
job_data = job_data.sort_values(['total','reviews','views'], ascending=False)
job_data['tfidf_data'] = [ast.literal_eval(job) for job in job_data['tfidf_data']]

# extract only the jobs which were posted today
today = datetime.datetime.now()
job_data['post_date_short'] = [job.date() for job in job_data['post_date']]
job_data = job_data[job_data['post_date_short']==today.date()]

# nan to none / is easier for ifs in jinja 
job_data = job_data.where(job_data.notnull(), None)

# time pasted
def time_pasted(date):
    try:
        diff_time = datetime.datetime.now() - date
        diff_hours = round(diff_time.total_seconds()/3600)
        if diff_hours==0:
            return str(diff_hours/60) + 'minutes ago'
        else:
            return str(diff_hours) + ' hours ago'
    except:
        return ""

job_data['time_pasted'] = [time_pasted(date) for date in job_data['post_date']]

# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-k", "--keywords", dest='keywords', help="define the keywords to search for", action='store')
parser.add_argument("-l", "--location", dest='location',help="define the location to search for", action='store')
parser.add_argument("-u", "--username", dest='username',help="Username for gmail account", action='store')
parser.add_argument("-p", "--password", dest='password',help="Password for gmail account", action='store')
parser.add_argument("-r", "--recipient", dest='recipient',help="Recipient for the mail", action='store')

# Read arguments from the command line
args = parser.parse_args()

# filter keywords and location
job_data = job_data[job_data['search_keywords']==args.keywords]
job_data = job_data[job_data['search_location']==args.location]

# convert dataframe to list of dicts
job_data = job_data.to_dict('records')

num_results = len(job_data)


app = Flask(__name__)

mail_settings = {
    'SERVER_NAME': 'smtp.gmail.com',
    'MAIL_SERVER':'smtp.gmail.com',
    'MAIL_PORT':465,
    'MAIL_USERNAME':args.username,
    'MAIL_PASSWORD':args.password,
    'MAIL_USE_TLS':False,
    'MAIL_USE_SSL':True
}
app.config.update(mail_settings)
mail = Mail(app)

if __name__ == '__main__':
    with app.app_context():
        msg = Message(subject=f'Job offerings for {today.strftime("%Y-%m-%d %H:%M:%S")}', 
                      sender = 'jonas.pirner93@gmail.com', 
                      recipients = [args.recipient])
        msg.html = render_template('mail.html', job_data=job_data, num_results=num_results, 
                                    search_keywords=args.keywords, search_location=args.location)
        mail.send(msg)