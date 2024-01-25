# Goals:
The target deliverables for this project are:
1. a basic search engine, including an index, page rank, & web crawler
2. a bayseian network constructed from high-ranked documents
3. the links in the bayesian network reference the documents that contributed to that link
4. a 'drunkards walk' is performed over the network to produce a string.
5. while walking the network, the documents that contribute to the link (retrieved from step 3) are recorded

Philosophically, this project is intended to be learning oriented; what we'd like to learn is whether we can add context to the results produced by generative AI.
This project is intended to be used as groundwork for a larger collection of personal, transparent,  Generative AI tools for web scraping.

Because we're more interested in learning something about the problem space, interesting discoveries should be discussed!

# General Description of Workflow
1. The Search Engine runs continuously
2. when page rank changes, the bayesian network is rebuilt
3. A user or other agent makes a query, through some interface
4. the markov process (drunkard's walk) produces a response string
  a. addditionally, a list of source documents is collected
  b. both the response string and source documents are returned to the user

# What we build:
1. the markovizer
2. the bayseian network
3. a basic querying interface

# what we configure/install
1. SOLR
2. Web Scraper (Notch or Scrappy)

# references, how we'll build
1. We'll use this guide to set up the search engine:
https://www.cs.toronto.edu/~muuo/blog/build-yourself-a-mini-search-engine/
2. we'll use this example code to help illustrate how to build markov chains from source text:
https://github.com/Trogluddite/codebro-bot/blob/master/markov.py
3. Markov chains: I think this is a good introduction
https://towardsdatascience.com/introduction-to-markov-chains-50da3645a50d 
4. There's a lot of overlap between Bayesian netowrks and markov chains (markov chains are a specific type of Bayeyian network).
I like this article for an introduction to Bayesian networks:
https://towardsdatascience.com/introduction-to-bayesian-networks-81031eeed94e 
5. The drunkards walk is used to traverse the bayesian network and produce a statistically weighted output. For text, following this process tends to produce language-like results because chains are only formed by words that follow other words.
this is a good description of that process: https://medium.com/i-math/the-drunkards-walk-explained-48a0205d304 
6. we're kinda just scratching the surface of the math -- we'll build a graph datastructure, with probabilities between nodes. The math is interesting and important, but we don't need to do a deep-dive for this demo
