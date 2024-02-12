#!/usr/bin/env python
import json

from numpy import random

from matrix_markov import MatrixMarkov

docs_map_path = "./test_docs/source_docs.json"

docs_json = dict()
with open(docs_map_path, 'r') as json_doc:
    docs_json = json.load(json_doc)

mm = MatrixMarkov()
for doc in [x for x in docs_json['documents']]:
    tf = doc['filename']
    src = doc['url']
    with open("./test_docs/"+ tf, 'r') as infile:
        contents = infile.read()
        mm.add_document(contents, src, defer_recalc=True)
mm.recalc_probabilities()

for _ in range(0,50):
    start_tok = random.choice( list(mm.token_index_map.keys()) )
    toks = mm.get_markov_chain(500, start_tok)
    print(" ".join(toks))

print(mm.tuple_to_source_map)

