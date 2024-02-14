#!/usr/bin/env python

from numpy import diag, matmul, matrix, pad, random, zeros

from string import punctuation

test_strings= [
        "hello, this is  the first sentence.",
        "this is the second sentence.",
        "my cat is weird",
        "why is my cat weird?",
        "my cat's breath smells like rabbit.",
        "hello, apple banana cheese rabbits.",
        "I like cheese but cheese does not like me.",
        "my cat tried to eat  these rabbits I'm rabbit sitting. hello this is cheese hello this isn't hello",
        "passion fruit is not orange, cheese is orange"
        ]


class MatrixMarkov:
    def __init__(self):
        self.token_index_map = dict()
        self.index_token_map = dict() # for when we want to look up by index ID (maybe use bidict lib?)
        self.transition_matx = matrix('0;0')
        self.tuple_to_source_map = dict()

        self._counts = zeros(shape=(0,0))
        self._prob_recalc_needed = False
        self._token_count = 0

    def add_document(self, ingest_text : str, source_ref : str = None, defer_recalc : bool = False):
        """
        adds tokens to the token_index_map, and re-counts transitions.

        for any series of tokens {t0, t1, t2 ... tN}, a 2-tuple (tN, tN+1)
        represents a transition. The counts matrix is a 2d column by row array
        and each transition is represented by the index value (from token_index_map)
        for tN (column) and tN+1 (row)

        for each transition (represented by a 2-tuple), we record a list (and counts)
        of documents that contributd to that link, in tuple_to_source_map

        by default, adding tokens recalulates transition probabilities, but that can
        be deferred by setting defer_recalc = True

        deferring probability recalc is desirable if we're batch-loading text
        """
        self._prob_recalc_needed = True

        # build or expand token -> index mapping
        input_toks = [x.strip(punctuation) for x in ingest_text.split()]
        for tok in input_toks:
            if self.token_index_map.get(tok, None) is None:
                self.token_index_map[tok] = self._token_count
                self.index_token_map[self._token_count] = tok
                self._token_count += 1
                self._counts = pad(self._counts, (0,1))

        transition_vect = [self.token_index_map[x] for x in input_toks]
        for i in range(0, len(input_toks) - 1):
            col = transition_vect[i+1]
            row = transition_vect[i]
            self._counts[col][row] = self._counts[col][row] + 1

        # build 2-tuple -> source ref counts
        for i in range(0, len(transition_vect) -1):
            if i == len(transition_vect) - 1:
                break
            trans_tuple = (transition_vect[i], transition_vect[i+1])
            if self.tuple_to_source_map.get(trans_tuple, None):
                if self.tuple_to_source_map[trans_tuple].get(source_ref, None):
                    self.tuple_to_source_map[trans_tuple][source_ref] += 1
                else:
                    self.tuple_to_source_map[trans_tuple] = {source_ref : 1}
            else:
                self.tuple_to_source_map[trans_tuple] = {source_ref : 1}

        # recalc transition matrix
        if not defer_recalc:
            self.recalc_probabilities()


    def recalc_probabilities(self):
        """
        rebuild the transition probability matrix, thusly:
            1. sum every 'count' column. Count's are matrix C
            2. each sum is converted to a probability between 0 and 1 with 1/sum
            3. form a diagonal matrix, D, from probabilities
            4. transition matrix T = DC
        """

        col_sums = self._counts.sum(axis=0)
        diag_matx = diag([(1/x if x != 0 else 0) for x in col_sums])
        self.transition_matx = matmul(self._counts, diag_matx)
        self._prob_recalc_needed = False


    def get_markov_chain(self, max_len : int, start_token : str):
        """
        do drunkard's walk over bayesian network
            1. get index of starting token
            2. get that column from the transition matrix
                this vector represents transittion probabilities from  the current token
            3. if the probabilities are 0, there is no transition from this token. Stop.
            4. otherwise, make a weighted random choice, and add that token to the list
            5. repeat until we've hit a stop or run down the iteration counter
            6. for each link, look up the source document & count

        """
        collected_toks = [start_token]
        collected_srcs = dict()

        curr_tok = start_token
        if self.token_index_map.get(curr_tok, None) is None:
            return  {'markov_chain' : [], 'sources': []}

        for _ in range(0,max_len):
            curr_tok_idx = self.token_index_map[curr_tok]
            probs_vect = self.transition_matx[:, curr_tok_idx]
            if sum(probs_vect) == 0: # the last token may not have a transtion
                break
            next_tok_idx = random.choice(list(self.index_token_map.keys()), p=probs_vect)

            # each link has a list of {source_url: count_of_contributions} dicts
            # dedupe those counts so that we have a count of contributions for the entire markov chain
            link_srcs = self.tuple_to_source_map[ (curr_tok_idx, next_tok_idx) ]
            for lk in link_srcs.keys():
                if collected_srcs.get(lk, None) is None:
                    collected_srcs[lk] = 0
                collected_srcs[lk] += link_srcs[lk]

            # prep next iter
            curr_tok = self.index_token_map[next_tok_idx]
            collected_toks.append(self.index_token_map[next_tok_idx])

        collected_toks[-1] = collected_toks[-1] + '.'
        retval = dict()
        retval['markov_chain'] = collected_toks
        retval['sources'] = collected_srcs
        return retval

    # useful for debugging
    def lookup_probs(self, token):
        token_idx = self.token_index_map.get(token, None)
        print(token_idx)
        if token_idx is None :
            print(f"token {token} does not exist in map")
            return
        probs_vect = self.transition_matx[:, token_idx]
        print(f'token: {token}, cum. probability: {sum(probs_vect)}')

        for idx, val in enumerate(probs_vect):
            if val > 0:
                print(f'idx: {idx}, val: {val}')

def main():
    mm = MatrixMarkov()
    for l in test_strings:
        mm.add_document(l, defer_recalc=True)
    mm.recalc_probabilities()
    for _ in range(0,20):
        toks = mm.get_markov_chain(20, random.choice(list(mm.token_index_map.keys())))

if __name__ == '__main__':
    main()
