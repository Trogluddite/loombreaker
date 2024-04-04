#!/usr/bin/env python

import requests
import json

def main():
  
    response = requests.get("http://20.84.107.89:8983/solr/nutch/select?fl=url%2Ccontent&indent=true&q.op=OR&q=nutch")
    print(response.status_code)
    parsed_json = response.json()  
    for doc in parsed_json["response"]["docs"]:
        print(doc["url"]) 

'''
    resp_url_0 = parsed_json['response']['docs']  # empty list
    # expected value in parsed_json['response']['docs']
    [ {"content" : "xyz", "url" : "http://"}]

    # what you'll want to do is:
    #1. iterate over that list
    #2. grab the URL, and the content
    #3. load that into a matrix_markov instance

    print(json.dumps(parsed_json))
    print(example_valid)
'''
if __name__ == '__main__':
    main()

