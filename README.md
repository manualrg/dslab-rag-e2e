# dslab-rag-e2e

# Prerequisites

Create a virtual environment
```bash
python -m venv .venv
```

Activate the Virtual Environment,
following the specific instructions for your OS,
for example, with Win/Powershell: `.\.venv\Scripts\activate`


Install dependencies
```bash
pip install -r requirements.txt
```

This virtual environment has been built using Win11 and Python 3.10.9, 3.11  and 3.12

As project is based in notebooks, three popular approaches can be followed:
* Install jupyter notebook: `pip install jupyter`
* Install jupyterlab: `pip install jupyterlab`
* Use VSCode notebooks extension: [Jupyter Notebooks in VS Code](https://code.visualstudio.com/docs/datascience/jupyter-notebooks) 
and install ipykernel with `pip install ipykernel`

As project is based in notebooks, three popular approaches can be followed:
* Install jupyter notebook: `uv add jupyter`
* Install jupyterlab: `uv add  jupyterlab`
* Use VSCode notebooks extension: [Jupyter Notebooks in VS Code](https://code.visualstudio.com/docs/datascience/jupyter-notebooks) 
and install ipykernel with `uv add  ipykernel`


## Enviroment Variables
Create a `.env` file and populate the following environment variables:
```
OPENAI_API_KEY=
QDRANT_API_KEY=
QDRANTL_URL=
```

Also, modify in `conf/infra.yaml` the `vdb_url` variable to point to your qdrant vector database 

# Data Folder
The data folder contains the following subfolders:
* raw:  files in regular extensions, like pdf
* interm: converted files to markdown and .json with optionally singular elements as images
* processed: chunks of several chunking experiments in .json format

This folder structure is inspired in: [Cookiecutter Data Science](https://cookiecutter-data-science.drivendata.org/)



# Scripts

**load_docs.py**
Scans a given path to ingest .md files into a VDB. It requieres access to:
* An embeddings model
* A VDB where the given documents are not present
```bash
uv run .\load_docs.py --index-name space
```


**rag.py**
Is both a script and a module with a RAG for basic QA. It requieres access to:
* A LLM
* An embeddings model
* A populated VDB
```bash
uv run .\rag.py --index-name space --retrieve-k 3
```


# Apps

**backend.py**
Basic chatbot backend
```bash
uv run uvicorn backend:app --reload
```
Go to http://localhost:8000/docs in your browser and check the swagger


**app.py**
Is a basic conversational interface built on `streamlit`. Get's the rag from rag.py
```bash
uv run streamlit run app.py
```
Go to http://localhost:8501/ in your browser


# Misc
**Get QA from a file**
I am giving you a document and you have to generate a set of 30 questions from the following dataset with the goal of evaluate a rag application. The questions must be classified by difficulty as: easy (direct answer from a single piece of text) medium hard 
Mimic the logic of the user regarding that edocument Return the questions in a csv format with the following columns: question, answer, difficulty, source, cite 
where the columns: 
source: is the section of the text where it appears 
cite: extract some literal text regarding the concepts used in the answer