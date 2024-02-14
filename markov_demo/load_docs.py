#!/usr/bin/env python
import json

from numpy import random

from matrix_markov import MatrixMarkov

docs_map_path = './test_docs/source_docs.json'

docs_json = dict()
with open(docs_map_path, 'r') as json_doc:
    docs_json = json.load(json_doc)

mm = MatrixMarkov()
for doc in [x for x in docs_json['documents']]:
    tf = doc['filename']
    src = doc['url']
    with open('./test_docs/'+ tf, 'r') as infile:
        contents = infile.read()
        mm.add_document(contents, src, defer_recalc=True)
mm.recalc_probabilities()

print('**GENERATING 10 MARKOV CHAINS**')
for _ in range(0,10):
    start_tok = random.choice( list(mm.token_index_map.keys()) )
    resp_dict = mm.get_markov_chain(100, start_tok)
    resp_string = " ".join(resp_dict['markov_chain'])

    sorted_citations = list()
    print(resp_string)
    for k, v in resp_dict['sources'].items():
        sort_tuple = (v, k)
        sorted_citations.append(sort_tuple)

    sorted_citations = sorted(sorted_citations, reverse=True)
    print("-> Top 3 Citations:")
    for i in range(0,3):
        if i >= len(sorted_citations):
            print(f"    Only {i} sources for this chain!" )
            break
        k,v = sorted_citations[i] # unpack tuple to reverse key,value order
        print(f'    {v}: {k} ')
    #print(f'source: {k}, contribution count: {v}')

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

