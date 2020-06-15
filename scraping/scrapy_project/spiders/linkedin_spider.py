import urllib
from datetime import datetime

import scrapy
from scrapy.shell import inspect_response
from w3lib.url import add_or_replace_parameter

from scrapy_project.convert_date import convert_date
from scrapy_project.items import JobItem


class LinkedinSpider(scrapy.Spider): 
    name = 'linkedin'

    start_urls = [ 
        'https://www.linkedin.com'   
    ]

    # set instance variable that counts how often class is called
    def __init__(self, keywords, location, filter_time):
        self.keywords = keywords # e.g. 'Data Scientist'
        self.location = location # e.g. 'Germany'
        self.filter_time =  filter_time 

        self.start_crawl = str(datetime.now())
        self.count = 1

        #scrapy crawl linkedin -a keywords="data scientist" -a location="germany" -a filter_time="false"

    def parse(self, response):
        base = 'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?'
        params = {'keywords':self.keywords,
                  'location':self.location,
                  # controls time filter; f_TP = 1 -> last 24 hours
                  'f_TP':self.filter_time, 
                  'start':0}
        # concat the url with params
        url = base + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        request = scrapy.Request(url=url, callback=self.parse_jobs)
        yield request

    def parse_jobs(self, response):
        self.logger.info('parse_job function called on %s', response.url)
        content = response.xpath('//*[contains(@class, "result-card job-result-card result-card")]')
        # Crawl site as long as there are results in content
        if len(content)>=1:
            # for every job on the current site
            for job_card in content:
                # any element, whereever that has the class ...__title
                title = job_card.xpath('.//*[@class="result-card__title job-result-card__title"]/text()').extract_first()
                # any element, whereever that has the class ..__location
                location = job_card.xpath('.//*[@class="job-result-card__location"]/text()').extract_first()
                # any element, whereever that has the class ..__listdate
                post_date = job_card.xpath('.//*[contains(@class, "job-result-card__listdate")]/text()').extract_first()
                # convert time string to real date
                post_date = str(convert_date(post_date))
                # gets stored in two different ways; is dependent on if there is a link about the company
                company_name = job_card.xpath('.//*[contains(@class, "result-card__subtitle job-result-card__subtitle")]/descendant-or-self::*/text()').extract_first()

                # follow the job link to get the description
                link = job_card.xpath('.//*[@class="result-card__full-card-link"]/@href').extract_first()

                request = scrapy.Request(url=link, callback=self.parse_description)

                # exclude refer id and other session specific parameters so that link becomes comparable
                link = urllib.parse.urlparse(link)
                link = link.netloc + link.path

                request.meta['location'] = location
                request.meta['title'] = title
                request.meta['post_date'] = post_date
                request.meta['company_name'] = company_name 
                request.meta['link'] = link 
                request.meta['start_crawl'] = self.start_crawl 
                request.meta['search_keywords'] = self.keywords
                request.meta['search_location'] = self.location 
                
                yield request
            # page count to next 25 results
            follow_url = add_or_replace_parameter(response.url, 'start', f'{self.count*25}')
            # increase counter
            self.count = self.count + 1

            yield response.follow(follow_url, callback=self.parse_jobs, meta={'dont_redirect': True})

    def parse_description(self, response):
        
        job = JobItem()

        description = response.xpath('//*[contains(@class, "description__text description__text")]').extract()[0]

        job['location'] = response.meta.get('location')
        job['title'] = response.meta.get('title')
        job['post_date'] = response.meta.get('post_date')
        job['company_name'] = response.meta.get('company_name') 
        job['link'] = response.meta.get('link') 
        job['start_crawl'] = response.meta.get('start_crawl') 
        job['search_keywords'] = response.meta.get('search_keywords')
        job['search_location'] = response.meta.get('search_location') 
        job['description'] = description

        criteria_responses = response.xpath('//ul[@class="job-criteria__list"]/li')
        job_criteria_list = []
        # get the job criteria which are probably a neccessary field for linkedin
        for criteria in criteria_responses:
            job_criteria = criteria.xpath('./span/text()').extract()
            # convert list to string
            job_criteria = "; ".join([criteria for criteria in job_criteria])
            # append list; has a fix order regarding to the site
            job_criteria_list.append(job_criteria)

        try:
            job['seniority_level'] = job_criteria_list[0]
        except IndexError:
            job['seniority_level'] = None 
        try:
            job['employement_type'] = job_criteria_list[1]
        except IndexError:
            job['employement_type'] = None 
        try:
            job['job_function'] = job_criteria_list[2]
        except IndexError:
            job['job_function'] = None 
        try:
            job['industries'] = job_criteria_list[3]
        except IndexError:
            job['industries'] = None 
        
        yield job
