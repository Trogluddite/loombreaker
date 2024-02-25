#!/usr/bin/env python
import requests
import json

from numpy import random

from matrix_markov import MatrixMarkov

response = requests.get("http://20.84.107.89:8983/solr/nutch/select?fl=url%2Ccontent&indent=true&q.op=OR&q=nutch")
docs_json = response.json()

mm = MatrixMarkov()

for doc in [x for x in docs_json['response']['docs']]:
    cont = doc['content']
    src = doc['url']
    mm.add_document(cont, src, defer_recalc=True)
mm.recalc_probabilities()

def get_paragraph():
    sentences = list()
    unsorted_citations = list()

    start_tok = random.choice( list(mm.token_index_map.keys()) )

    resp_dict = mm.get_markov_chain(100, start_tok)
    resp_dict['markov_chain'][0] = "    " + resp_dict['markov_chain'][0]
    sentences.append(" ".join(resp_dict['markov_chain']))

    unsorted_citations = unsorted_citations + list(dict(resp_dict['sources']).items())

    for _ in range(0, random.randint(5, 15)):
        start_tok = random.choice( list(mm.token_index_map.keys()) )
        resp_dict = mm.get_markov_chain(100, start_tok)
        sentences.append(" ".join(resp_dict['markov_chain']))
        unsorted_citations = unsorted_citations + list(dict(resp_dict['sources']).items())

    resp = { 'sentences' : list(), 'citations' : list() }
    resp['sentences'] = sentences
    resp['citations'] = unsorted_citations
    return resp

def dedupe_and_sort_citations(citation_list: list) -> list:
    uniq_references = dict()

    for ref in citation_list:
        if uniq_references.get(ref[0], None):
            uniq_references[ref[0]] = uniq_references[ref[0]] + ref[1]
        else:
            uniq_references[ref[0]] = ref[1]

    sorted_citations = list()
    for k, v in uniq_references.items():
        sort_tuple = (v, k)
        sorted_citations.append(sort_tuple)

    sorted_citations = sorted(sorted_citations, reverse=True)
    return [{v:k} for k, v in sorted_citations]

paragraph_data = get_paragraph()
top_citations = dedupe_and_sort_citations(paragraph_data['citations'])[0:3]
paragraph_text = " ".join(paragraph_data['sentences'])

print(paragraph_text)
print("-> Top 3 Citations:")
for i in range(0,3):
    if i >= len(top_citations):
        print(f"    Only {i} sources for this chain!" )
        break
    k, v = list(top_citations[i].items())[0] # unpack tuple to reverse key,value order
    print(f'    {k}: {v} ')

#print(mm.transition_matx)
#print(mm.token_index_map)
#print(mm.index_token_map)
#print(mm._counts)
#for token in mm.token_index_map.keys():
#print(mm.lookup_probs('and'))

#nprint("transition matrix:")
#print(mm.transition_matx)
#print("lookup table")
#print(mm.token_index_map)

