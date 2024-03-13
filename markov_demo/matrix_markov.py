#!/usr/bin/env python
"""
    A class for building Bayeseian Networks and retreivinig Markov chains
    MatrixMarkov uses bigrams/2-grams; optionally, references are recorded
"""
import math
import re

from numpy import diag, matmul, matrix, pad, random, zeros


START_TOK = "<START>"
STOP_TOK = "<STOP>"


class MatrixMarkov:
    """
    * build, or add to, a Bayeseian network
    * every token is given a unique index ID in token_index_map
    * every index has a token, looked ups in index_token_map
    * n-grams are n=2.
    * Every n1=>n2 transition is a column,row pair in the _counts matrix
    * probability of any token n=1 joning n=2 in the bigram is in the
      transition matrix
    * for every bigram, a tuple is used to key tuple_to_source_map
    * when a document is ingested, its source key count is incremnted
      for each bigram it contributs to the weights.
    """

    def __init__(self):
        self.token_index_map = {}
        self.index_token_map = {}
        self.transition_matx = matrix('0;0')
        self.tuple_to_source_map = {}

        # expect the first document to have about 5k unique tokens;
        # we'll over-allocate (hopefully), expand if needed, then
        # trim down to size when we're done.
        self._pad_size = 5000
        self._counts = zeros(shape=(self._pad_size, self._pad_size))
        self._prob_recalc_needed = False
        self._token_count = 0

        self._doc_ingestion_time_total = 0

    def add_document(
            self,
            ingest_text: str,
            source_ref: str = None,
            defer_recalc: bool = False):
        """
        adds tokens to the token_index_map, and re-counts transitions.

        by default, adding tokens recalulates transition probabilities, but that can
        be deferred by setting defer_recalc = True

        deferring probability recalc is desirable if we're batch-loading text
        """
        self._prob_recalc_needed = True

        # build or expand token -> index mapping
        clean_text = self.clean_input(ingest_text)
        input_toks = self.tokenize_input(clean_text)
        for tok in input_toks:
            # expand the array by about half the token count if we don't have space
            # we'll have some slack; we'll trim it later
            if self._token_count+1 >= self._pad_size:
                self._pad_size = self._pad_size + (math.floor(self._pad_size / 2))
                self._counts = pad(self._counts, (0, self._pad_size))
            if self.token_index_map.get(tok, None) is None:
                self.token_index_map[tok] = self._token_count
                self.index_token_map[self._token_count] = tok
                self._token_count += 1

        # vector indexes for each token; n, n+1 pairs represent bigrams
        transition_vect = [self.token_index_map[x] for x in input_toks]
        for i in range(0, len(input_toks) - 1):
            col = transition_vect[i + 1]
            row = transition_vect[i]
            self._counts[col][row] = self._counts[col][row] + 1

        # trim array down to square of len(self._token_count)
        self._counts = self._counts[0:self._token_count, 0:self._token_count]
        self._pad_size = self._token_count

        # build 2-tuple -> source ref counts
        for i in range(0, len(transition_vect) - 1):
            if i == len(transition_vect) - 1:
                break
            trans_tuple = (transition_vect[i], transition_vect[i + 1])
            if self.tuple_to_source_map.get(trans_tuple, None):
                if self.tuple_to_source_map[trans_tuple].get(source_ref, None):
                    self.tuple_to_source_map[trans_tuple][source_ref] += 1
                else:
                    self.tuple_to_source_map[trans_tuple] = {source_ref: 1}
            else:
                self.tuple_to_source_map[trans_tuple] = {source_ref: 1}

        # recalc transition matrix
        if not defer_recalc:
            self.recalc_probabilities()

    def clean_input(self, input_text: str):
        """
        remove meta-text and other non-semantic tokens, based on some guesses
        about what such should be removed
        """
        input_text = re.sub(r'--', ' ', input_text)
        input_text = re.sub('[\[].*?[\]]', '', input_text)
        input_text = re.sub(r'(\b|\s+\-?|^\-?)(\d+|\d*\.\d+)\b','', input_text)
        return input_text

    def tokenize_input(self, input_text: str):
        """
        add arbitrary start/stop tokens to indicate beginning and end of statements
        parses based on hard stops, which are assumed too be ?!. and newline
        FUTURE: this is a pre-procssing method; pipeline this
        """
        words = []
        lines = input_text.split('\n')
        for line in lines:
            tokens = line.split()
            if len(tokens) == 0:
                continue
            tokens[len(tokens) - 1] = tokens[len(tokens) - 1].strip(".?!")
            tokens = [START_TOK] + tokens + [STOP_TOK]
            indexes_with_stops = [
                tokens.index(x) for x in tokens if x.strip(".?!") != x]
            for i in indexes_with_stops[::-1]:
                tokens[i] = tokens[i].strip(".?!")
                tokens.insert(i + 1, STOP_TOK)
                tokens.insert(i + 2, START_TOK)
            words += tokens
        return words

    def recalc_probabilities(self):
        """
        rebuild the transition probability matrix, thusly:
            1. sum every 'count' column. Count's are matrix C
            2. each sum is converted to a probability between 0 and 1 with 1/sum
            3. form a diagonal matrix, D, from probabilities
            4. transition matrix T = DC
        """
        col_sums = self._counts.sum(axis=0)
        diag_matx = diag([(1 / x if x != 0 else 0) for x in col_sums])
        self.transition_matx = matmul(self._counts, diag_matx)
        self._prob_recalc_needed = False


    def get_markov_chain(self, max_len: int, start_token: str):
        """
        returns a dict: {'markov_chan' : ['list','of','tokens']
                         'sources' : [ {source_url: count_of_contributions}]
                         }
        does a drunkard's walk over bayesian network
            1. get index of starting token
            2. get that column from the transition matrix
                this vector represents transittion probabilities from  the current token
            3. if the probabilities are 0, there is no transition from this token. Stop.
            4. otherwise, make a weighted random choice, and add that token to the list
            5. repeat until we've hit a stop or run down the iteration counter
            6. for each link, look up the source document & count
            7. remove any syntax cues (like START/STOP tokens), add punctuation
        FUTURE: post-processing should be a separate method; pipeline this
        """
        collected_toks = [start_token]
        collected_srcs = {}

        curr_tok = start_token
        if self.token_index_map.get(curr_tok, None) is None:
            return {'markov_chain': [], 'sources': []}

        for _ in range(0, max_len):
            curr_tok_idx = self.token_index_map[curr_tok]
            probs_vect = self.transition_matx[:, curr_tok_idx]
            if sum(probs_vect) == 0:  # the last token may not have a transtion
                break
            next_tok_idx = random.choice(
                list(self.index_token_map.keys()), p=probs_vect)

            # each link has a list of {source_url: count_of_contributions} dicts
            # dedupe those counts so that we have a count of contributions for
            # the entire markov chain
            link_srcs = self.tuple_to_source_map[(curr_tok_idx, next_tok_idx)]
            for lk in link_srcs.keys():
                if collected_srcs.get(lk, None) is None:
                    collected_srcs[lk] = 0
                collected_srcs[lk] += link_srcs[lk]

            # prep next iter
            curr_tok = self.index_token_map[next_tok_idx]
            if curr_tok == STOP_TOK:
                break
            collected_toks.append(self.index_token_map[next_tok_idx])

        collected_toks = [tok for tok in collected_toks if tok != START_TOK]
        collected_toks[-1] = collected_toks[-1].strip(' ') + '.'
        collected_toks[0] = collected_toks[0][0].upper() + \
            collected_toks[0][1:]

        retval = {}
        retval['markov_chain'] = collected_toks
        retval['sources'] = collected_srcs
        return retval

    def lookup_probs(self, token):
        """
        intendeed to be used for debugging or other metrics
        given any token n=1, look up the probability of the n=2 token
        forming the bigram
        """
        token_idx = self.token_index_map.get(token, None)
        print(token_idx)
        if token_idx is None:
            print(f"token {token} does not exist in map")
            return
        probs_vect = self.transition_matx[:, token_idx]
        print(f'token: {token}, cum. probability: {sum(probs_vect)}')

        for idx, val in enumerate(probs_vect):
            if val > 0:
                print(f'idx: {idx}, val: {val}')


def main():  # pylint: disable=missing-function-docstring
    pass


if __name__ == '__main__':
    main()
