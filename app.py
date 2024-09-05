import streamlit as st
from llama_index.legacy.llms import OpenAI
import openai
from llama_index.legacy import SimpleDirectoryReader
from tempfile import NamedTemporaryFile
import os
from llama_index.legacy import VectorStoreIndex
from llama_index.legacy import ServiceContext
from llama_index.legacy import Document


st.set_page_config(page_title="Chat with the HR AI Chatbot 🤖",
                   layout="centered", initial_sidebar_state="auto", menu_items=None)
openai.api_key = "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"
st.title("HR AI Chatbot 🤖")

if "messages" not in st.session_state.keys():  # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me a question!"}
    ]


@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading and indexing the docs – hang tight! This should take 1-2 minutes."):
        reader = SimpleDirectoryReader(input_dir="./data", recursive=True)
        docs = reader.load_data()
        service_context = ServiceContext.from_defaults(llm=OpenAI(
            model="gpt-4", temperature=0.8, system_prompt="You are an expert on the HR documents. Please provide detailed insights from the HR documents on [specific topic or question]."))
        index = VectorStoreIndex.from_documents(
            docs, service_context=service_context)
        return index


index = load_data()
# chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True, system_prompt="You are an expert on the HR documents and your job is to answer technical questions. Assume that all questions are related to the HR documents provided. Keep your answers technical and based on facts – do not hallucinate features.")

if "chat_engine" not in st.session_state.keys():  # Initialize the chat engine
    st.session_state.chat_engine = index.as_chat_engine(
        chat_mode="condense_question", verbose=True)

# Prompt for user input and save to chat history
if prompt := st.chat_input("Your question"):
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages:  # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.chat_engine.chat(prompt)
            st.write(response.response)
            message = {"role": "assistant", "content": response.response}
            # Add response to message history
            st.session_state.messages.append(message)
