import os
import json
import asyncio
import logging
from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Annotated, Optional
import nest_asyncio

from openai import AsyncOpenAI
from llama_index.core import VectorStoreIndex, Settings, ChatPromptTemplate
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.vector_stores.milvus import MilvusVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai_like import OpenAILike
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.postprocessor.llm_rerank import LLMRerank

from NF_Agent.services.utils import update_system_prompt, restrict_to_json_format
from NF_Agent.core.config import chat_llm_settings, embedding_model_settings, agent_settings, milvus_settings

nest_asyncio.apply()
chat_llm = OpenAILike(api_base=chat_llm_settings.CHAT_LLM_BASE_URL,
                      api_key=chat_llm_settings.CHAT_LLM_API_KEY,
                      model=chat_llm_settings.CHAT_LLM_MODEL,
                      # max_tokens=1024,
                      context_window=3900,
                      is_chat_model=True,
                      is_function_calling_model=True,
                      )

embed_model = OpenAIEmbedding(api_base=embedding_model_settings.EMBEDDING_MODEL_BASE_URL,
                              api_key=embedding_model_settings.EMBEDDING_MODEL_API_KEY,
                              model_name=embedding_model_settings.EMBEDDING_MODEL)

Settings.llm = chat_llm
Settings.embed_model = embed_model
Settings.chunk_size = agent_settings.BM25_CHUNK_SIZE
Settings.chunk_overlap = agent_settings.BM25_CHUNK_OVERLAP

vector_store = MilvusVectorStore(uri=agent_settings.MILVUS_URI + "/database/" + agent_settings.MILVUS_DB_NAME,
                                 collection_name=agent_settings.MILVUS_COLL_NAME,
                                 dim=embedding_model_settings.embedding_dim,
                                 overwrite=False,
                                 enable_sparse=False,
                                 embedding_field=milvus_settings.embedding_field,
                                 similarity_metric=milvus_settings.similarity_metric,
                                 index_config=milvus_settings.index_config,
                                 )

milvus_index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
milvus_retriever = milvus_index.as_retriever(similarity_top_k=milvus_settings.similarity_top_k)

bm25_retriever = BM25Retriever.from_persist_dir(agent_settings.BM25_PERSIST)

retriever = QueryFusionRetriever(retrievers=[milvus_retriever,
                                             bm25_retriever
                                             ],
                                 retriever_weights=[0.6, 0.4],
                                 similarity_top_k=milvus_settings.similarity_top_k,
                                 num_queries=4,
                                 use_async=True,
                                 mode="dist_based_score"
                                 )

ranker = LLMRerank(choice_batch_size=10, top_n=3)

chat_llm_client = AsyncOpenAI(base_url=chat_llm_settings.CHAT_LLM_BASE_URL,
                              api_key=chat_llm_settings.CHAT_LLM_API_KEY
                              )

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
with open(os.path.join(parent_dir, "api/agents/routers/prompts/rag/user_query_expansion.txt")) as f:
    user_query_expansion_prompt = f.read()

with open(os.path.join(parent_dir, "api/agents/routers/prompts/rag/summarize_rag.txt")) as f:
    summarization_prompt = f.read()


async def expand_user_query(messages):
    task_messages = update_system_prompt(messages=messages, system_prompt=user_query_expansion_prompt)
    response = await chat_llm_client.chat.completions.create(model=chat_llm_settings.CHAT_LLM_MODEL,
                                                             messages=task_messages,
                                                             stream=False,
                                                             temperature=chat_llm_settings.temperature,
                                                             top_p=chat_llm_settings.top_p
                                                             )
    try:
        result = json.loads(response.choices[0].message.content)
    except:
        response = await restrict_to_json_format(llm_client=chat_llm_client,
                                                 llm_settings=chat_llm_settings,
                                                 messages=task_messages
                                                 )
        result = json.loads(response.choices[0].message.content)

    return result


async def summarize_rag_result(rag_result, expanded_user_query):
    task_prompt = summarization_prompt.format(retrieval_result=str(rag_result),
                                              user_query=expanded_user_query,
                                              )
    task_messages = [{"role": "user", "content": task_prompt}]
    response = await chat_llm_client.chat.completions.create(model=chat_llm_settings.CHAT_LLM_MODEL,
                                                             messages=task_messages,
                                                             stream=False,
                                                             temperature=chat_llm_settings.temperature,
                                                             top_p=chat_llm_settings.top_p
                                                             )
    result = response.choices[0].message.content
    return result


async def retrieval_milvus_BM25(messages):
    expanded_user_query = await expand_user_query(messages)
    expanded_user_query = expanded_user_query["expanded_user_query"]
    retrieved_results = await retriever.aretrieve(expanded_user_query)

    # Postprocess retrieved results using ranker
    # retrieved_results_list = list(retrieved_results)  # Avoid re-awaiting
    # print(retrieved_results_list)
    reranked_retrieval_results = ranker.postprocess_nodes(retrieved_results, query_str=expanded_user_query)
    # Process reranked results
    retrieved_text = [item.get_content() for item in reranked_retrieval_results]
    retrieval_result = await summarize_rag_result(rag_result=retrieved_text, expanded_user_query=expanded_user_query)
    return retrieval_result


if __name__ == '__main__':
    messages = [
        {"role": "user", "content": "What is the total proposed Gross Internal Area (GIA) for 99 Bishopsgate?"},
    ]
    asyncio.run(retrieval_milvus_BM25(messages=messages))
