# src/chain.py

import streamlit as st

# FINAL FIX: Use the V1 root import for memory, which is the most stable shim.
from langchain.memory import ConversationBufferWindowMemory 

# Keep other packages on their canonical V2 imports
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

from src.config_loader import CONFIG, ConfigLoader

# --- Memory Setup (rest of file is stable) ---
def get_session_memory():
    msgs = StreamlitChatMessageHistory(key="chat_messages")
    k_window = CONFIG.get_config['memory']['message_window']
    memory = ConversationBufferWindowMemory(
        k=k_window,
        chat_memory=msgs,
        memory_key="history",
        return_messages=True
    )
    return memory, msgs

# --- Chain Setup ---
def get_conversational_chain():
    if "llm_chain" not in st.session_state:
        model_name = CONFIG.get_config['model']['identifier']
        temp = CONFIG.get_config['model']['temperature']
        openai_api_key = ConfigLoader.get_api_key("OPENAI_API_KEY")

        llm = ChatOpenAI(
            model=model_name,
            temperature=temp,
            api_key=openai_api_key,
        )

        system_message = (
            "You are a helpful customer support chatbot for the 'GenAI Journey' project. "
            "Your goal is to provide concise, accurate, and professional answers. "
            "If asked about topics outside of support or GenAI, politely refuse and "
            f"state you are limited to support functions. Forbidden topics: {CONFIG.get_config['safety']['forbidden_topics']}."
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ])
        
        chain = (
            RunnablePassthrough.assign(history=lambda x: x["history"].load_memory_variables({})["history"])
            | prompt
            | llm
            | StrOutputParser()
        )
        st.session_state.llm_chain = chain

    return st.session_state.llm_chain

def run_chain(user_input: str):
    chain = get_conversational_chain()
    memory, msgs = get_session_memory()
    response = chain.invoke({"input": user_input, "history": memory})
    memory.save_context({"input": user_input}, {"output": response})
    return response