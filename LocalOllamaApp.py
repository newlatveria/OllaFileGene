import streamlit as st
import requests
import json

# --- Page Configuration ---
st.set_page_config(page_title="Ollama API Controller", layout="wide")
st.title("🤖 Ollama API Dashboard")

# --- Sidebar: Input Variables ---
st.sidebar.header("Configuration")
model_name = st.sidebar.text_input("MODEL_NAME", value="localmodel")
api_url = st.sidebar.text_input("API_URL", value="http://localhost:11434/api/generate")
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7)
stream_response = st.sidebar.checkbox("Stream Output", value=True)

# --- Main Interface ---
user_prompt = st.text_area("Enter your prompt:", placeholder="e.g., Analyze the code in this directory...")

if st.button("Run Command"):
    if not user_prompt:
        st.warning("Please enter a prompt first.")
    else:
        # Construct the JSON payload (like the -d flag in curl)
        payload = {
            "model": model_name,
            "prompt": user_prompt,
            "stream": stream_response,
            "options": {
                "temperature": temperature
            }
        }

        st.subheader("Output")
        output_placeholder = st.empty()
        full_response = ""

        try:
            # Equivalent to: curl -X POST [api_url] -d [payload]
            with requests.post(api_url, json=payload, stream=stream_response) as response:
                response.raise_for_status()
                
                if stream_response:
                    for line in response.iter_lines():
                        if line:
                            chunk = json.loads(line.decode('utf-8'))
                            full_response += chunk.get("response", "")
                            output_placeholder.markdown(full_response + "▌")
                    output_placeholder.markdown(full_response) # Remove cursor at end
                else:
                    result = response.json()
                    st.write(result.get("response", "No response field found."))

        except requests.exceptions.RequestException as e:
            st.error(f"API Error: {e}")

# --- Debug: View the 'curl' Command ---
with st.expander("View equivalent curl command"):
    curl_cmd = f"""
    curl {api_url} \\
    -d '{{
        "model": "{model_name}",
        "prompt": "{user_prompt}",
        "stream": {str(stream_response).lower()},
        "options": {{ "temperature": {temperature} }}
    }}'
    """
    st.code(curl_cmd, language="bash")
