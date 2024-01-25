# Goals:
The target deliverables for this project are:
1. a basic search engine, including an index, page rank, & web crawler
2. a bayseian network constructed from high-ranked documents
3. the links in the bayesian network reference the documents that contributed to that link
4. a 'drunkards walk' is performed over the network to produce a string.
5. while walking the network, the documents that contribute to the link (retrieved from step 3) are recorded

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
