The following is the architecture diagram of the NF Agent:

![NF_Agent.png](/mnt/demo_data_1/gawain/python_code/NF_Agent/figure/NF_Agent.png)

The NF Agent is composed of four key modules: Supervisor, Execution, Evaluation, and Aggregation.

## Supervisor Module

**Function:** Determines which sub-agents are required to retrieve the necessary information to accurately respond to the user's query.

## Execution Module

**Function:** Concurrently executes all sub-agents identified by the Supervisor module.

### Web Search Sub-Agent

**Function:** Conducts web searches using DuckDuckGo to gather up-to-date information from the internet.

### RAG (Retrieval-Augmented Generation) Sub-Agent

**Function:** Performs document retrieval using LlamaIndex on content stored in a VectorDB, utilizing provided documents and PDFs.

### Database Query Sub-Agent

**Function:** Queries the database containing the current planning status information.

## Evaluation Module

**Function:** Evaluates whether additional web searches are necessary to supplement the initial results. If further information is required, this module formulates the appropriate search queries and initiates additional web searches.

## Aggregation Module

**Function:** Consolidates information from all executed sub-agents, synthesizing and generating a cohesive, final response for the user.

