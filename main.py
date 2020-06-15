import re
import sqlite3

import numpy as np
import pandas as pd
from tqdm import tqdm

from kununu_ratings import get_kununu_rating
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer


def load_data():
    # load data from table
    job_df = pd.read_sql_table('jobs_table','sqlite:///scraping/jobs.db')
    return job_df

def job_preprocessing(job_df):
    # strip html
    TAG_RE = re.compile(r'<[^>]+>')
    def remove_tags(text):
        return TAG_RE.sub('', text)
    # convert post_date to date
    job_df['post_date'] = pd.to_datetime(job_df['post_date'], errors='coerce')
    # create clean desc
    job_df['description_text'] = [remove_tags(job) for job in job_df['description']]
    # small description to display
    job_df['small_desc'] = [job[:400] + '...' for job in job_df['description_text']]
    # split location fields
    job_df[['city','state','country']] = job_df['location'].str.split(',', expand=True)
    ### Create tfidf words
    german_stop_words = stopwords.words('german')
    english_stop_words = stopwords.words('english')
    vect = TfidfVectorizer(stop_words=german_stop_words + english_stop_words, max_df=0.9)
    tfidf = vect.fit_transform(job_df['description_text'])
    feature_names = vect.get_feature_names()
    tfidf_df = pd.DataFrame(tfidf.toarray(), columns=feature_names).T
    # create tfidf top list; each list is a post and each dict contains
    # the top n most important words with their tfidf score
    tfidf_data = []
    # how many words should be considered
    N = 5
    for i,_ in enumerate(tfidf_df):
        tfidf_data.append(tfidf_df.iloc[:,i].sort_values(ascending=False)[:N].to_dict())
    
    job_df['tfidf_data'] = tfidf_data
    job_df['tfidf_data'] = job_df['tfidf_data'].astype(str)

    job_df.to_sql('jobs_preprocessed_table', 'sqlite:///scraping/jobs.db', if_exists='replace')

    return job_df

def get_ratings(job_df):
    RELEVANT_FIELDS = ['city','company_name', 'name','reviews','total','views','logo','latlon','rating_level']
    # company_df - stores the old entries 
    conn = sqlite3.connect('scraping/jobs.db')
    curr = conn.cursor()
    # create company rating db
    curr.execute(''' CREATE TABLE IF NOT EXISTS company_ratings (city TEXT, 
                                                                 company_name TEXT, 
                                                                 name TEXT, 
                                                                 reviews INTEGER, 
                                                                 total FLOAT, 
                                                                 views INTEGER,
                                                                 logo TEXT,
                                                                 latlon TEXT,
                                                                 rating_level TEXT)''')
    stored_companies = curr.execute(''' SELECT *
                                        FROM company_ratings ''').fetchall()
    # print number of entries in db
    print(f'Number of entries in searched companies db: {len(stored_companies)}')
    # convert to df
    stored_companies_df = pd.DataFrame(stored_companies, columns= RELEVANT_FIELDS)
    # tuples to search for
    companies_df = job_df.groupby(['city','company_name'])['title'].count().reset_index()
    # anti join to exclude the results both in search_companies_df and db
    companies_df = pd.merge(companies_df, stored_companies_df, how='outer', indicator=True, on=['company_name','city'])
    search_companies_df = companies_df[companies_df['_merge']=='left_only']
    companies_df = companies_df[companies_df['_merge']=='right_only']
    # if no new companies
    if len(search_companies_df)<1:
        return print('No new companies to look for')
    # print unique number of companies which are used for search
    print(f'Search for {len(search_companies_df)} new unique companies')
    results = []
    # search the rating for each unique company location pair
    for company, location in tqdm(zip(search_companies_df['company_name'], search_companies_df['city'])):
        res = get_kununu_rating(company=company, location=location)
        if res != None:
            res['city'] = location
            res['company_name'] = company
        results.append(res)
    percent_found = np.round((len([res for res in results if res != None]) / len(results))*100)
    print(f'For {percent_found} % information has been found')
    # stores all the found information from kununu
    rating_df = pd.DataFrame.from_records([res for res in results if res != None])
    # if no ratings have been found merge would fail
    if len(rating_df)<1:
        return print('No information for searched companies found')
    # merge the kununu information
    company_rating_df = pd.concat([rating_df[RELEVANT_FIELDS], companies_df])
    # store the tuples which will be tried in db
    company_rating_df[RELEVANT_FIELDS].to_sql('company_ratings', con=conn, if_exists='append', index=False)

    return company_rating_df

def main():
    print('='*80)
    print('Loading the data')
    print('='*80)
    job_df = load_data()

    print('Preprocessing')
    print('='*80)
    job_df = job_preprocessing(job_df)

    print('Get company ratings')
    print('='*80)
    company_df = get_ratings(job_df)

if __name__ == "__main__":
    main()
