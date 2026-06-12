import streamlit as st
import httpx
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.styles import inject_css, page_header, api_url

st.set_page_config(page_title="Financial Chat | Wealth Advisor", page_icon="💬", layout="wide")
inject_css()

page_header("Financial Assistant", "Ask questions about your spending, savings, or investments.", "💬")

user_id = 1

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Fetch from backend
    try:
        with httpx.Client(timeout=10) as client:
            resp = client.get(api_url("chat/history"), params={"user_id": user_id})
            if resp.status_code == 200:
                history = resp.json()
                for msg in history:
                    st.session_state.messages.append({"role": msg["role"], "content": msg["content"]})
    except Exception:
        pass
        
    if not st.session_state.messages:
        st.session_state.messages.append({"role": "assistant", "content": "Hi! I'm your AI Financial Assistant. How can I help you today?"})

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Quick Prompts
col1, col2, col3, col4 = st.columns(4)
quick_prompts = [
    "Analyze my recent spending",
    "How can I save more?",
    "What is my risk profile?",
    "Suggest investment options"
]

prompt_clicked = None
for i, col in enumerate([col1, col2, col3, col4]):
    with col:
        if st.button(quick_prompts[i], use_container_width=True):
            prompt_clicked = quick_prompts[i]

# React to user input
user_input = st.chat_input("Ask a financial question...")
prompt = prompt_clicked or user_input

if prompt:
    # Display user message
    st.chat_message("user").markdown(prompt)
    # Add to session state
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display assistant response with spinner
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Thinking..."):
            try:
                with httpx.Client(timeout=30) as client:
                    response = client.post(
                        api_url("chat/"),
                        json={"user_id": user_id, "message": prompt}
                    )
                    if response.status_code == 200:
                        full_response = response.json().get("assistant_message", "I'm sorry, I couldn't process that.")
                        message_placeholder.markdown(full_response)
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                    else:
                        st.error("Error communicating with the assistant.")
            except httpx.RequestError:
                st.error("Backend server is unreachable.")
