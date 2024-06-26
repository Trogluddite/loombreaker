#!/usr/bin/env python

''' Example code to exercise the MatrixMarkov class '''
import requests
import json

from math import sqrt
from numpy import array, dot, random

from matrix_markov import MatrixMarkov

SOLR_QUERY_TIMEOUT = 180
SOLR_URL = "http://20.84.107.89:8983/solr/"
SOLR_QUERY = "nutch/select?fl=content%2Ctitle%2Curl&fq=url%3A%22https%3A%2F%2Fen.m.wikipedia.org*%22&indent=true&q.op=OR&q=Lithium"
STATIC_QUERY_STR = f"{SOLR_URL}{SOLR_QUERY}"

response = requests.get(
    STATIC_QUERY_STR,
    timeout=180)
docs_json = response.json()

mm = MatrixMarkov()

for doc in list(docs_json['response']['docs']):
    cont = doc['content']
    src = doc['url']
    mm.add_document(cont, src, defer_recalc=True)
mm.recalc_probabilities()


def get_paragraph():
    ''' make a fake "paragraph" from markov data, includes list of citations '''
    sentences = []
    unsorted_citations = []

    start_tok = random.choice(list(mm.token_index_map.keys()))

    resp_dict = mm.get_markov_chain(100, start_tok)
    resp_dict['markov_chain'][0] = "    " + resp_dict['markov_chain'][0]
    sentences.append(" ".join(resp_dict['markov_chain']))

    unsorted_citations = unsorted_citations + \
        list(dict(resp_dict['sources']).items())

    for _ in range(0, random.randint(2, 3)):
        start_tok = random.choice(list(mm.token_index_map.keys()))
        resp_dict = mm.get_markov_chain(100, start_tok)
        sentences.append(" ".join(resp_dict['markov_chain']))
        unsorted_citations = unsorted_citations + \
            list(dict(resp_dict['sources']).items())

    resp = {'sentences': [], 'citations': []}
    resp['sentences'] = sentences
    resp['citations'] = unsorted_citations
    return resp


def dedupe_and_sort_citations(citation_list: list) -> list:
    ''' remove duplicate citation keys and fold counts into new references dict '''
    uniq_references = {}

    for ref in citation_list:
        if uniq_references.get(ref[0], None):
            uniq_references[ref[0]] = uniq_references[ref[0]] + ref[1]
        else:
            uniq_references[ref[0]] = ref[1]

    sorted_citations = []
    for k, v in uniq_references.items(): # pylint: disable=redefined-outer-name
        sort_tuple = (v, k)
        sorted_citations.append(sort_tuple)

    sorted_citations = sorted(sorted_citations, reverse=True)
    return [{v: k} for k, v in sorted_citations]

def get_cos_similarity(target : str, compareTo : str):
    search_tokens = list(set(target.split() + compareTo.split()))
    targetCounts = {}
    for k in search_tokens:
        targetCounts[k] = target.count(k)
    compareToCounts = {}
    for k in search_tokens:
        compareToCounts[k] = compareTo.count(k)

    target_vect = array([targetCounts[x] for x in targetCounts.keys()])
    compare_to_vect = array([compareToCounts[x] for x in compareToCounts.keys()])
    num = dot(target_vect, compare_to_vect)
    denom = sqrt(target_vect.dot(target_vect)) * sqrt(compare_to_vect.dot(compare_to_vect))

    return num/denom

match_this =  "ionic sulfur impurities and especially but only in their chlorides"
target_score = 0.85
best_match_score = 0.0
worst_match_score = 1.0
best_match_paragraph = {}
worst_match_paragraph = {}
iter = 0
max_iters = 500

while best_match_score < target_score and iter < max_iters:
    p = get_paragraph()
    similarity = get_cos_similarity(match_this, " ".join(p['sentences']))
    if similarity > best_match_score:
        print(f'new best match score is {similarity}, on iter: {iter}')
        best_match_score = similarity
        best_match_paragraph = p
    if similarity < worst_match_score:
        worst_match_score = similarity
        worst_match_paragraph = p
    iter += 1
    if iter % 50 == 0:
        print(f"completed iter {iter}")

top_citations = dedupe_and_sort_citations(best_match_paragraph['citations'])[0:3]

clean_search_result = {}
clean_search_result['text'] = " ".join(best_match_paragraph['sentences'])
clean_search_result['top_citations'] = top_citations

print(f"best/worst matches for match_string: {match_this}")
print(f"worst_match_score is: {worst_match_score}")
print(" ".join(worst_match_paragraph['sentences']))

print('\n')
print(f"best_maatch_score is: {best_match_score}")
print(" ".join(best_match_paragraph['sentences']))
print("-> Top 3 Citations:")
for i in range(0, 3):
    if i >= len(top_citations):
        print(f"    Only {i} sources for this chain!")
        break
    # unpack tuple to reverse key,value order
    k, v = list(top_citations[i].items())[0]
    print(f'    {k}: {v} ')


raw_json_blob = json.dumps(best_match_paragraph)
clean_json_blob = json.dumps(clean_search_result)
print("\nRaw Result JSON")
print(raw_json_blob)
print("\nClean & Deduped JSON")
print(clean_json_blob)
