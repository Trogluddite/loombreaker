# loombreaker
CS-480 Capstone Project

This project is intended to test some ideas around:
* topic-specific search engines
* Generative AI with transparent training
* Generative AI with citations
* peer-networking for topic-specific search engines

#### Luddites & Loom Breaking
In the modern era, the Luddites are typically associated with anti-technology and anti-progress stances.
Reality is more complex -- automated looms shifted the balance between labor and capital ownership during the industrial revolution.
Breaking looms was, arguably, one of very few tactics that laborers could use to advocate for fair working conditions.

If you believe the fourth industrial revolution has arrived, one hopes that democratizing powerful tools can help maintain a healthier balance between capital ownership and the needs of individuals.

Within the scope of CS-480, the target deliverables are:
1. a custom search engine is configured using open source indexing & crawling tools
2. documents from the search engine are ingested into markov a bayseian network with links to source docs
3. markov chains are produced with ranked lists of source documents.

Everything beyond that is a stretch goal.


## Problems with web search
* Web search is optimized with profit incentives
* Public search engines are opaque, generalized, and also have profit incentives
* Search engines need to handle the _whole_ web, so the resource requirements are huge.

## Problems with Generative AI
* Generated results are focused on aesthetics – a ‘conversational’ response is given higher weight than an accurate response.
* Opacity: There’s no real way for an end-user to understand how the result is produced from a training set
* Obfuscation: There’s no way to cite or credit authors of source material, and no way to validate correctness without pre-existing knowledge or parallel (non-AI) research
* Entropic degeneration (potential?): Generative AI is producing results that are presented on the web, and the web is the primary source of training data for most generative AI.

## Potential approaches
Note: philosophically, there should be a heavy emphasis on involving human intelligence in the tool-chain – we’re less interested in aesthetics and more interested in using the AI tools produce intermediate solutions that humans will refine.

### Generative AI w/ citations
#### Topic-specific search engines
* tunable spider
* tunable page rank
* Tunable index (only index what’s relevant to the topic)

#### Generative search, simplest formation
* Simplest formation: the documents in the index are ingested into a weighted markov chain
* A result string produced with a weighted random-walk over the target markov chain
* Each link in the chain includes a sorted list of sources that include that chain
* The result string includes a ranked list of sources, giving some statistical data (percentage source) for each
* Result set may or may not resemble what the user is interested in; expect user to repeat search until a result looks like what they want
* Quasi-literate gibberish common from markov chains

#### First iterative improvement: user-guided retraining
* Use the approach above, but the user up/down votes the results, and the weights of the markov chain are adjusted appropriately

#### Second iterative improvement: GANs
* User provides an example that resembles what they want to know
* GANs train the markov set
* This should be semi-supervised – users should have an opportunity to review generator output and determine if the example is meaningful

#### Third iterative improvement: Attention & Transformers for summarization
?? I need to know more about how this works.

#### Fourth Iterative Improvment: retreival augmented generation
* feedback to spider/scraper
* feedback to page rank

###  Federated Indexing
* Public interface for topic-specific searches
* The index publishes a list of topics
* May include some statistics about topic categories – to start, these are set by humans; over time, categorization from AI tools may take over
* Document-rank may be used to select “top ‘N’” documents; documents are delivered to peer; peer does its own generative search.
* When filtering (let’s not call it ‘searching’), the topic-specific engine will source documents or insights in this order:
  * self
  * Peer topic indexes
  * The open web

* First iterative improvement: user-guided analysis of peer-quality – peer indexes are searched by weight, based on the quality of results as identified by users.
* Second iterative improvement: GAN to rank peer indexers
* Third iterative improvement: indexers publish … statistics about how their chains are formed? How?
