import requests
import pandas as pd
import numpy as np
import urllib


def get_kununu_rating(company, location, first_iter=True):
    # define common terms; sometimes search term or kununu company has unnecessary GmbH 
    # which confuses the search 
    COMMON_TERMS = ['gmbh','ag','dach']
    THRESHOLD = 0.3
    
    base = 'https://api.kununu.com/v1/search/profiles?'
    # set api parameter to current tuple
    params = {'page':1,
              'per_page':18,
              'q':company,
              'location':location}
    if first_iter==False:
        del params['location'] 
    # concat the url with params
    url = base + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    # create the request
    r = requests.get(url, headers={'Referer':'https://www.kununu.com/us/search', 
                                    'Accept':'application/vnd.kununu.v1+json;version=2016-05-11', 
                                    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'})
    request_data = r.json()

    input_company_list = company.split(' ')
    input_company_set = set([word.lower() for word in input_company_list if word not in COMMON_TERMS])
    
    # do the following iteration as long as found is not True
    found = False
    
    try:
        # first best solution: everything is the same
        for profile in request_data['profiles']:
            res_company_list = profile['name'].lower().split(' ')
            res_company_set = [word for word in res_company_list if word not in COMMON_TERMS]

            overlap = input_company_set.intersection(res_company_set)
            len(overlap) / len(input_company_set)

            if (len(overlap) / len(input_company_set))>THRESHOLD and profile['city'].lower()==location.lower():
                found = True
                profile['rating_level'] = 'match'
                profile['kununu_link'] = url
                return profile
        # next best solution: same name but 'all' location
        if found == False:
            for profile in request_data['profiles']: 
                res_company_list = profile['name'].lower().split(' ')
                res_company_set = [word for word in res_company_list if word not in COMMON_TERMS]

                overlap = input_company_set.intersection(res_company_set)
                len(overlap) / len(input_company_set)
                
                if (len(overlap) / len(input_company_set))>THRESHOLD and profile['city']=='all':
                    found = True
                    profile['rating_level'] = 'all'
                    profile['kununu_link'] = url
                    return profile
        # next best solution: same name but different location
        if found == False:
            for profile in request_data['profiles']: 
                res_company_list = profile['name'].lower().split(' ')
                res_company_set = [word for word in res_company_list if word not in COMMON_TERMS]

                overlap = input_company_set.intersection(res_company_set)
                len(overlap) / len(input_company_set)
                
                if (len(overlap) / len(input_company_set))>0.8:
                    found = True
                    profile['rating_level'] = 'different location'
                    profile['kununu_link'] = url
                    return profile

        # try all options without the location once again
        if first_iter==True:
                return get_kununu_rating(company=company, location=location, first_iter=False)
        
        pass
    # if nothing works    
    except:
        pass