import os
import uuid

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")

st.set_page_config(
    page_title="Headwy Bank Support",
    page_icon="🏦",
    layout="centered",
)

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("Headwy Bank Support")
st.caption("AI assistant for loans, cards, and banking FAQs — powered by RAG")

with st.sidebar:
    st.subheader("Settings")
    api_override = st.text_input("Backend URL", value=API_URL)
    if api_override:
        API_URL = api_override.rstrip("/")

    st.text(f"Session: {st.session_state.session_id}")

    if st.button("New conversation"):
        st.session_state.session_id = str(uuid.uuid4())[:8]
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.info(
        "💡 **First time loading?** Because this app uses Render's free hosting tier, "
        "the backend service completely powers down during inactivity. "
        "Please allow up to **60 seconds** for the initial spin-up. If you see an error "
        "below, just give it a minute and refresh your page!"
    )
    st.divider()
    st.subheader("Upload document")
    uploaded = st.file_uploader("PDF or TXT", type=["pdf", "txt"])
    if uploaded and st.button("Upload to knowledge base"):
        with st.spinner("Indexing document..."):
            try:
                r = requests.post(
                    f"{API_URL}/upload",
                    files={"file": (uploaded.name, uploaded.getvalue())},
                    timeout=120,
                )
                r.raise_for_status()
                st.success(r.json())
            except Exception as e:
                st.error(f"Upload failed: {e}")

    try:
        health = requests.get(f"{API_URL}/health", timeout=10).json()
        st.caption(f"API: {health.get('status')} | Chunks in DB: {health.get('documents_indexed')}")
    except Exception:
        st.warning("Backend not reachable. Start API with: uvicorn backend.main:app --reload")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            st.caption("Sources: " + ", ".join(msg["sources"]))

if prompt := st.chat_input("Ask about loans, cards, policies..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("_Thinking..._")
        try:
            resp = requests.post(
                f"{API_URL}/chat",
                json={
                    "message": prompt,
                    "session_id": st.session_state.session_id,
                },
                timeout=90,
            )
            resp.raise_for_status()
            data = resp.json()
            answer = data.get("answer", "No response.")
            sources = data.get("sources", [])
            placeholder.markdown(answer)
            if sources:
                st.caption("Sources: " + ", ".join(sources))
            st.session_state.messages.append(
                {"role": "assistant", "content": answer, "sources": sources}
            )
        except requests.exceptions.HTTPError as e:
            detail = "Request failed"
            try:
                detail = e.response.json().get("detail", detail)
            except Exception:
                pass
            placeholder.error(detail)
            st.session_state.messages.append(
                {"role": "assistant", "content": f"Error: {detail}"}
            )
        except Exception as e:
            placeholder.error(f"Could not reach backend: {e}")
            st.session_state.messages.append(
                {"role": "assistant", "content": f"Error: {e}"}
            )
