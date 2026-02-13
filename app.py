import streamlit as st
import requests

from src import conf


# Configuration
API_URL = "http://127.0.0.1:8000/"
try:
    conf_settings = conf.load(file="settings.yaml")
    index_name = conf_settings.vdb_index
    retrieve_k = conf_settings.retrieve_k
except Exception as e:
    index_name = "space"
    retrieve_k = 3


def save_feedback(index):
    st.session_state.messages[index]["feedback"] = st.session_state[f"feedback_{index}"]


st.set_page_config(page_title="Assistant", page_icon="💬")

st.title("💬 Chatbot")

# --- Sidebar controls ---
with st.sidebar:
    st.header("Settings")
    st.write(f"Index: {index_name}")
    st.write(f"Retrieve k: {retrieve_k}")

if st.sidebar.button("Reset chat"):
    st.session_state.messages = []
    st.rerun()

# --- Initialize chat history in session_state
if "messages" not in st.session_state:
    st.session_state.messages = []


# --- Instanciate RAG in monolithic set ups
# from rag import main as rag_agent_builder
# @st.cache_resource 
# def load_agent():
#     rag_graph = rag_agent_builder(
#             index_name=index_name,
#             retrieve_k=retrieve_k,
#         )
#     return rag_graph

# rag_graph = load_agent()


# --- Display chat history
for i, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])
        # Add feedback
        feedback = msg.get("feedback", None)  #Dislay button
        st.session_state[f"feedback_{i}"] = feedback
        st.feedback(
            "thumbs",
            key=f"feedback_{i}",
            #disabled=feedback is not None,
            on_change=save_feedback,
            args=[i],
        )


# --- Chat input
if prompt := st.chat_input("Ask a question about your knowledge base…"):
    # Save user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Generate reply
    payload = {
        "message": prompt
    }

    resp = requests.post(API_URL + "chat/", json=payload)
    #rag_graph.invoke(...)
    reply = resp.json()['response'] # str
    ctx = resp.json()['context'] # List[str]
    

    # Save and show reply
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.chat_message("assistant").write(reply)
    if ctx:
        with st.expander(f"Context ({len(ctx)})"):
            for i, doc in enumerate(ctx, 1):
                snippet = doc[:200]
                st.markdown(f"**Chunk: {i}**")
                st.write(snippet + ("…" if len(doc) > 200 else ""))
