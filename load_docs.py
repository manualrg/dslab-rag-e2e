"""
from .md files from input-dir to the VBD index `index-name`
"""
import os
import sys
import uuid
import argparse
import logging
from pathlib import Path
from typing import Iterable, List, Tuple

from dotenv import load_dotenv
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from src import utils, conf


logger = logging.getLogger(__name__)

# Constants
headers_to_split_on = [
    ("#", "Header 1"),
    # ("##", "Header 2"),
    # ("###", "Header 3"),
]



def discover_markdown_files(input_dir: Path) -> List[Path]:
    files = sorted(input_dir.rglob("*.md"))
    logger.info("Discovered %d markdown file(s) under %s", len(files), input_dir)
    if not files:
        logger.warning("No .md files found in %s. Nothing to ingest.", input_dir)
    return files


def load_markdown(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8")
        if not text.strip():
            logger.warning("File is empty: %s", path)
        return text
    except Exception as e:
        logger.error("Failed reading %s: %s", path, e)
        raise


def mk_docs_from_files(paths: Iterable[Path]) -> List[Document]:
    docs: List[Document] = []
    for p in paths:
        text = load_markdown(p)
        docs.append(Document(page_content=text, metadata={"title": p.name, "path": str(p)}))
    logger.info("Loaded %d Document(s)", len(docs))
    return docs


def split_markdown_docs(
    docs: List[Document],
    headers_to_split_on: List[Tuple[str, str]],
    chunk_size: int,
    chunk_overlap: int,
) -> List[Document]:
    if not docs:
        return []

    logger.info("Splitting by Markdown headers: %s", headers_to_split_on)
    md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on, strip_headers=False)

    by_headers: List[Document] = []
    for d in docs:
        parts = md_splitter.split_text(d.page_content)  # no split_document
        by_headers.extend(parts)

    logger.info("Header splits produced %d chunk(s)", len(by_headers))

    logger.info("Splitting by RecursiveCharacterTextSplitter: chunk_size=%d, chunk_overlap=%d",
                chunk_size, chunk_overlap)
    char_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    splits = char_splitter.split_documents(by_headers)
    logger.info("Final split produced %d chunk(s) total", len(splits))

    # Light telemetry
    if splits:
        lengths = [len(s.page_content) for s in splits]
        logger.info("Chunk length stats (chars): min=%d avg=%.1f max=%d",
                    min(lengths), sum(lengths) / len(lengths), max(lengths))
    else:
        logger.warning("No splits were produced")


    # Exercise: Can really short chunks be created? Should be maintain them?
    # Can we easily fix it?

    return splits



def main(
        index_name,
        chunk_size ,
        chunk_overlap,
        input_dir
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
    
    EMBEDDINGS = conf_settings.embeddings
    EMB_DIM = conf_settings.embeddings_dim  
    VDB_URL = conf_infra.vdb_url

    logger.info("Loaded Configurtion")


    # Paths
    path_input = utils.path_data / input_dir
    logger.info("Input path: %s", path_input.as_posix())


    # Clients
    embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY, model=EMBEDDINGS)
    try:
        _ = embeddings.embed_query("healthcheck")
        logger.info("OpenAI embeddings healthcheck OK")
    except Exception as err:
        logger.error("Embeddings healthcheck failed: %s", err)
        sys.exit(2)

    client_qdrant = QdrantClient(api_key=QDRANT_API_KEY, url=VDB_URL)
    try:
        _ = client_qdrant.get_collections()
        logger.info("Qdrant connectivity OK")
    except Exception as err:
        logger.error("Qdrant connectivity failed: %s", err)
        sys.exit(2)


    if not input_dir.exists():
        logger.error("Input directory does not exist: %s", input_dir)
        sys.exit(2)

    files = discover_markdown_files(input_dir)
    if not files:
        sys.exit(0)


    # Prepare data
    docs = mk_docs_from_files(files)  #List[Documents] -> File
    splits = split_markdown_docs(
        docs=docs,
        headers_to_split_on=headers_to_split_on,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )   #List[Documents] -> Chunk

    if not splits:
        logger.warning("No chunks produced; exiting.")
        sys.exit(0)

    # Index
    if not client_qdrant.collection_exists(index_name):
        client_qdrant.create_collection(
            collection_name=index_name,
            vectors_config=VectorParams(
                size=EMB_DIM,
                distance=Distance.COSINE),
        )

    vector_store = QdrantVectorStore.from_existing_collection(
        embedding=embeddings,
        collection_name=index_name,
        url=VDB_URL,
        api_key=QDRANT_API_KEY
    )  # Optional, can use vdb client directly

    uuids = [str(uuid.uuid4()) for _ in range(len(splits))]
    vector_store.add_documents(documents=splits, ids=uuids)
    logger.info("Completed. Total chunks upserted: %d", len(splits))

    try:
        _ = vector_store.similarity_search("healthcheck")
        logger.info("Qdrant search healthcheck OK")
    except Exception as err:
        logger.error("Qdrant search failed: %s", err)
        sys.exit(2)


# ---------- CLI ----------
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest Markdown files into Qdrant.")
    parser.add_argument("--index-name", required=True, help="Qdrant collection name.")
    parser.add_argument("--chunk-size", type=int, default=2048, help="Character chunk size (default: 2048).")
    parser.add_argument("--chunk-overlap", type=int, default=256, help="Character chunk overlap (default: 256).")
    parser.add_argument("--input-dir", type=Path, default="data/pipeline", help="Directory to search for .md files. Defaults to data/pipeline.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    utils.setup_logging()

    main(
        index_name=args.index_name,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        input_dir=args.input_dir
    )