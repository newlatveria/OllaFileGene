import streamlit as st
import requests

def render_automation(api_url, model_name):
    task = st.text_input("Describe scheduled task")
    if st.button("Generate Cron"):
        r = requests.post(f"{api_url}/api/generate",
                          json={"model": model_name,
                                "prompt": f"Crontab line for: {task}",
                                "stream": False})
        st.code(r.json().get("response", ""))
