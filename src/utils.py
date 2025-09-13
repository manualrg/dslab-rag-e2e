from typing import List
from pathlib import Path
import os
import sys
import logging
import pandas as pd
from langchain_core.documents import Document


logger = logging.getLogger(__name__)


def example():
    logger.info("utls.example")
    print("utls.example")

def testing_example():
    return "Hello World"

# ################# PATHS
path_root = Path(os.getcwd())
# Folders for data/
path_data = path_root / "data"
path_data_raw = path_data / "raw"
path_data_interim = path_data / "interim"
path_data_processed = path_data / "processed"

# Other Folders 
path_conf = path_root / "conf"
path_models = path_root / "models"
path_logs = path_root / "logs"
path_outputs = path_root / "outputs"



# ################# LOGS
def setup_logging(level=logging.INFO):
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)


# ################# INITIALIZATION
def create_folders():
    path_conf.mkdir(parents=True, exist_ok=True)
    path_data.mkdir(parents=True, exist_ok=True)
    path_data_raw.mkdir(parents=True, exist_ok=True)
    path_data_interim.mkdir(parents=True, exist_ok=True)
    path_data_processed.mkdir(parents=True, exist_ok=True)


# UTILS
def corpus_stats(encoding, corpus: List[Document]) -> pd.Series:
    lst_docs = [encoding.encode(doc.page_content) for doc in corpus]
    data = [len(x) for x in lst_docs]
    return pd.Series(data)