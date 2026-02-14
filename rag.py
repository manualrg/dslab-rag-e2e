import os
import sys
import argparse
import logging
from typing import List, TypedDict
from functools import partial
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_qdrant import QdrantVectorStore
from langchain_core.prompts import ChatPromptTemplate

from langgraph.graph import START, StateGraph
from src import utils, conf



# Graph definition
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str

def format_docs(docs):
    return "\n\n".join([d.page_content for d in docs])


def retrieve(state: State, vector_store, retrieve_k):
    retrieved_docs = vector_store.similarity_search(state["question"], k=retrieve_k)
    return {"context": retrieved_docs}


def generate(state: State, llm, prompt):
    docs_content = format_docs(state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content}



def build_rag(
        vector_store,
        llm,
        retrieve_k
):
    
    prompt_template = """Answer the question based only on the following context:
    ```
    {context}
    ```
    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(prompt_template)


    g = StateGraph(State)
    # from functools import partial
    # Use partial to create an argument-populated version of node funtcions
    # retrieve(state: State, vector_store, retrieve_k) -> retrieve(state: State)
    g.add_node("retrieve", partial(retrieve, vector_store=vector_store, retrieve_k=retrieve_k))
    g.add_node("generate", partial(generate, llm=llm, prompt=prompt))

    g.set_entry_point("retrieve")
    g.add_edge("retrieve", "generate") 


    agent = g.compile()

    return agent


def main(
        index_name: str,
        retrieve_k: int
    ):

    # Logging
    logger = logging.getLogger(__name__)

    # Environment variables
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

    if not OPENAI_API_KEY:
        logger.error("Missing OPENAI_API_KEY")
        sys.exit(2)
    if not QDRANT_API_KEY:
        logger.error("Missing QDRANT_API_KEY")
        sys.exit(2)
    logger.info("Loaded environment variables")

    # Configuration
    try:
        conf_settings = conf.load(file="settings.yaml")
        conf_infra = conf.load(file="infra.yaml")
    except Exception as e:
        logger.error("Failed to load conf files: %s", e)
        sys.exit(2)
    
    LLM_WORKHORSE = conf_settings.llm_workhorse
    EMBEDDINGS = conf_settings.embeddings
    VDB_URL = conf_infra.vdb_url

    logger.info("Loaded Configuration")


    # Clients
    llm = ChatOpenAI(
        api_key=OPENAI_API_KEY,
        model=LLM_WORKHORSE,
        )
    try:
        llm.invoke("tell me a joke about devops")
    except Exception as err:
        print(err)
        
    embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY, model=EMBEDDINGS)
    try:
        _ = embeddings.embed_query("healthcheck")
        logger.info("OpenAI embeddings healthcheck OK")
    except Exception as err:
        logger.error("Embeddings healthcheck failed: %s", err)
        sys.exit(2)


    vector_store = QdrantVectorStore.from_existing_collection(
        embedding=embeddings,
        collection_name=index_name,
        url=VDB_URL,
        api_key=QDRANT_API_KEY,
    )  # Optional, could use native client implementation
    try:
        _ = vector_store.asimilarity_search("healthcheck")
        logger.info("Qdrant search healthcheck OK")
    except Exception as err:
        logger.error("Qdrant search failed: %s", err)
        sys.exit(2)

    logger.info("Loaded Clients with Langchain abstractions")


    rag_graph = build_rag(
        vector_store,
        llm,
        retrieve_k
    )
    logger.info("Built RAG Graph")

    return rag_graph


# ---------- CLI ----------
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest Markdown files into Qdrant.")
    parser.add_argument("--index-name", required=True, help="Qdrant collection name.")
    parser.add_argument("--retrieve-k", type=int, default=3, help="Character chunk size (default: 3).")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    utils.setup_logging()

    rag_graph = main(
        index_name=args.index_name,
        retrieve_k=args.retrieve_k,
    )

    question = "¿A qué distancia de la Tierra está el sistema Althéra?"
    resp = rag_graph.invoke({"question": question})
    
    context = resp['context']
    answer = resp['answer']

    print(f"{question=}")
    print(f"{answer=}")
    print("-"*10, "contexts retrieved:", "-"*10)
    for i, doc in enumerate(context):
        print("Chunk: {i}")
        print(doc.page_content)