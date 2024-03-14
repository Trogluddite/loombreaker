#!/usr/bin/env python

''' Example code to exercise the MatrixMarkov class '''
import requests

from numpy import random

from matrix_markov import MatrixMarkov


SOLR_QUERY_TIMEOUT = 180
SOLR_URL = "http://20.84.107.89:8983/solr/"
SOLR_QUERY = "nutch/select?fl=content%2Ctitle%2Curl&fq=url%3A%22https%3A%2F%2Fen.m.wikipedia.org*%22&indent=true&q.op=OR&q=Argon"
STATIC_QUERY_STR = f"{SOLR_URL}{SOLR_QUERY}"

response = requests.get(STATIC_QUERY_STR, timeout=SOLR_QUERY_TIMEOUT)
docs_json = response.json()

mm = MatrixMarkov()

clean_text = mm.clean_input(docs_json['response']['docs'][0]['content'])
print(clean_text)
