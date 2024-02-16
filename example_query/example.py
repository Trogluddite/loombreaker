#!/usr/bin/env python

import requests
import json


## curl-d '
## { "query" : "nutch", "fields" : "url,content" }'
def main():
    data = { "query" : "true", "fields" : "url,content" }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    response = requests.get("http://20.84.107.89:8983/solr/nutch/query", headers=headers, data=data)
    print(response.status_code)

    parsed_json = json.loads(response.content)  # object type should be dict
    print(type(parsed_json))  # you can check the type


    resp_url_0 = parsed_json['response']['docs']  # empty list
    # expected value in parsed_json['response']['docs']
    [ {"content" : "xyz", "url" : "http://"}]

    # what you'll want to do is:
    #1. iterate over that list
    #2. grab the URL, and the content
    #3. load that into a matrix_markov instance

    print(json.dumps(parsed_json))
    print(example_valid)

if __name__ == '__main__':
    main()

