# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JobItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    company_name = scrapy.Field()
    post_date = scrapy.Field()
    location = scrapy.Field()
    description = scrapy.Field()
    link = scrapy.Field()
    start_crawl = scrapy.Field()
    search_keywords = scrapy.Field()
    search_location = scrapy.Field()
    seniority_level = scrapy.Field()
    employement_type = scrapy.Field()
    job_function = scrapy.Field()
    industries = scrapy.Field()
