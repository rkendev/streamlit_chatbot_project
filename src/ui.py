from __future__ import annotations

from typing import Dict, List

import streamlit as st

from src.chatbot import AppConfig, Chatbot, load_config


def get_history() -> List[Dict[str, str]]:
    """Return chat history from Streamlit session state."""
    if "history" not in st.session_state:
        st.session_state.history = []
    return st.session_state.history


def get_bot(config: AppConfig) -> Chatbot:
    """Create the chatbot once and keep it in session state."""
    if "bot" not in st.session_state:
        st.session_state.bot = Chatbot(config)
    return st.session_state.bot


def render_chat(history: List[Dict[str, str]]) -> None:
    """Render existing messages from history."""
    for msg in history:
        role = msg.get("role", "assistant")
        content = msg.get("content", "")
        with st.chat_message(role):
            st.markdown(content)


def main() -> None:
    config = load_config()

    st.set_page_config(
        page_title=config.app_title,
    )

    st.title(config.app_title)
    st.caption(f"Version {config.app_version}")

    st.info(
        "This assistant focuses on software development, data work, and AI assisted workflows. "
        "It cannot help with unsafe or restricted topics."
    )
    
    # side bar controls
    with st.sidebar:
        st.subheader("Session")
        if st.button("New chat", use_container_width=True):
            st.session_state.history = []
            st.rerun()

    history = get_history()
    render_chat(history)

    st.caption(
        "Note: conversations are logged locally in logs/chat_log.csv for debugging and quality checks."
    )

    user_input = st.chat_input("Type your question here")

    if user_input:
        # show user message immediately
        history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        bot = get_bot(config)

        # show assistant reply
        with st.chat_message("assistant"):
            with st.spinner("Thinking"):
                answer = bot.answer(history=history, user_message=user_input)
                st.markdown(answer)

        history.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()
