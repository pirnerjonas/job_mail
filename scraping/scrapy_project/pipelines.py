# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


import sqlite3
from scrapy.exceptions import DropItem

class DatabasePipeline(object):

    def __init__(self):
        self.create_connection()
        self.create_table()

    def create_connection(self):
        self.conn = sqlite3.connect('jobs.db')
        self.curr = self.conn.cursor()

    def create_table(self):
        # try to create jobs table
        try:
            self.curr.execute("""create table jobs_table(
                                    title text,
                                    location text,
                                    post_date text,
                                    company_name text,
                                    description text,
                                    link text,
                                    start_crawl text,
                                    search_keywords text,
                                    search_location text,
                                    seniority_level text,
                                    employement_type text,
                                    job_function text,
                                    industries text 
                                )""")
        except sqlite3.OperationalError as e:
            print(e)

    def process_item(self, item, spider):
        # only store it in database if it is not already in there
        same_links = self.curr.execute("""SELECT * FROM jobs_table WHERE link=?""",(item['link'],)).fetchall()
        # if the link is not available in the db; create insert
        if len(same_links)<1:
            self.store_db(item)
            return item
        else:
            raise DropItem(f'Duplicate job found: {item}')


    def store_db(self, item):
        self.curr.execute("""INSERT INTO jobs_table VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",(
            item['title'],
            item['location'],
            item['post_date'],
            item['company_name'], 
            item['description'],
            item['link'],
            item['start_crawl'],
            item['search_keywords'],
            item['search_location'],
            item['seniority_level'],
            item['employement_type'],
            item['job_function'],
            item['industries']
        ))
        self.conn.commit()
