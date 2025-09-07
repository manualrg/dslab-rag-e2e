# dslab-rag-e2e

# Prerequisites

(Optional, you may have installed uv in your main python installation)
Install uv: [Installing uv](https://docs.astral.sh/uv/getting-started/installation/#pypi)

Check uv installation:
```bash
uv --help
```

Create a uv project on the current project folder, given the project specification
```bash
uv sync
```
This will create a Virtual Environment called .venv


Activate the Virtual Environment,
following the specific instructions for your OS,
for example, with Win/Powershell: `.\.venv\Scripts\activate`

This will create a virtual environment in .venv folder and some files and install the dependencies especifed in uv project files: [Project structure and files](https://docs.astral.sh/uv/concepts/projects/layout/)


Donwload `docling` models (if not automatically done):
```bash
docling-tools models download
```
The model artifacts are downloaded by default in `$HOME/.cache/docling/models`

This virtual environment has been built using Win11 and Python 3.10.9, 3.11  
There is a unresolved issue on Win OS [OSError: could not find or load spatialindex_c-64.dll](https://github.com/docling-project/docling/issues/867)
that may affect you.

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
MISTRAL_API_KEY=
```


# Data Folder
The data folder contains the following subfolders:
* raw:  files in regular extensions, like pdf
* interm: converted files to markdown and .json with optionally singular elements as images
* processed: chunks of several chunking experiments in .json format

This folder structure is inspired in: [Cookiecutter Data Science](https://cookiecutter-data-science.drivendata.org/)

[Doing RAG on PDFs using File Search in the Responses API](https://cookbook.openai.com/examples/file_search_responses)