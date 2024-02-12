#!/usr/bin/env python

from numpy import diag, matmul, matrix, random, zeros

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
        self.transition_matx = matrix('0;0')

        self._counts = zeros(shape=(0,0))
        self._prob_recalc_needed = False
        self._token_count = 0

    def add_document(self, ingest_text : str, defer_recalc : bool = False):
        """
        adds tokens to the token_index_map, and re-counts transitions.

        for any series of tokens {t0, t1, t2 ... tN}, a 2-tuple (tN, tN+1)
        represents a transition. The counts matrix is a 2d column by row array
        and each transition is represented by the index value (from token_index_map)
        for tN (column) and tN+1 (row)

        by default, adding tokens recalulates transition probabilities, but that can
        be deferred by setting defer_recalc = True

        deferring probability recalc is desirable if we're batch-loading text
        """
        self._prob_recalc_needed = True
        input_toks = [x.strip(punctuation) for x in ingest_text.split()]
        for tok in input_toks:
            if self.token_index_map.get(tok, None) is None:
                self.token_index_map[tok] = self._token_count
                self._token_count += 1
        self._counts.resize((self._token_count, self._token_count), refcheck=False)
        transition_vect = [self.token_index_map[x] for x in input_toks]
        for i in range(0, len(input_toks) - 1):
            self._counts[transition_vect[i+1]][transition_vect[i]] += 1
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

        """
        collected_toks = [start_token]
        curr_tok = start_token

        for _ in range(0,max_len):
            curr_tok_idx = self.token_index_map[curr_tok]
            probs_vect = self.transition_matx[:, curr_tok_idx]
            probs_vect /= probs_vect.sum() # normalize so sum is within numpy tolerance
            if sum(probs_vect) != 1: # the last token may not have a transtion
                break
            next_tok = random.choice(list(self.token_index_map.keys()), p=probs_vect)
            curr_tok = next_tok
            collected_toks.append(next_tok)
        stop_char = random.choice(['.', '!', '?' ])
        collected_toks[-1] = collected_toks[-1] + stop_char
        return collected_toks

def main():
    mm = MatrixMarkov()
    for l in test_strings:
        mm.add_document(l, defer_recalc=True)
    mm.recalc_probabilities()
    for _ in range(0,20):
        toks = mm.get_markov_chain(20, random.choice(list(mm.token_index_map.keys())))
        print(" ".join(toks))

if __name__ == '__main__':
    main()
