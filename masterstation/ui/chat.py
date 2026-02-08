import streamlit as st
import requests
from core.session import save_session

def render_chat(api_url, model_name, options):
    for m in st.session_state["messages"]:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("Message AI..."):
        st.session_state["messages"].append(
            {"role": "user", "content": prompt})

        payload = {
            "model": model_name,
            "messages": st.session_state["messages"],
            "options": options,
            "stream": False,
        }

        try:
            r = requests.post(f"{api_url}/api/chat", json=payload)
            r.raise_for_status()
            ans = r.json()["message"]["content"]
        except Exception as e:
            ans = f"Error: {e}"

        st.session_state["messages"].append(
            {"role": "assistant", "content": ans})
        save_session()
        st.rerun()
