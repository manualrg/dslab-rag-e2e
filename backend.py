from typing import List
from fastapi import FastAPI
from pydantic import BaseModel

from rag import main as rag_builder
from src import conf


# Configuration
try:
    conf_settings = conf.load(file="settings.yaml")
    index_name = conf_settings.vdb_index
    retrieve_k = conf_settings.retrieve_k
except Exception as e:
    index_name = "space"
    retrieve_k = 3

# Initialization
rag_graph = rag_builder(
    index_name=index_name,
    retrieve_k=retrieve_k,
)

app = FastAPI(
    title="Simple Chatbot API",
    description="A basic API for QA chatbot."
)

# Data model
class MessageInput(BaseModel):
    message: str
    # user?
    # topic?

class ChatResponse(BaseModel):
    response: str
    context: List[str]
    # sources?
    # relevancy?

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/chat/", response_model=ChatResponse)
def chat(input_message: MessageInput):
    """
    Receives a user message and returns a simple, predefined response.
    This is a basic, rule-based chatbot implementation.
    """
    message = input_message.message.lower().strip()
    
    resp = rag_graph.invoke({"question": message})
    
    context = resp['context']
    answer = resp['answer']

    return {"response": answer, "context": [x.page_content for x in context]}
