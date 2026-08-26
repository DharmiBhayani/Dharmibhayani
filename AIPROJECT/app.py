import streamlit as st
from config.config import APP_NAME
from database.database import initialize_database

initialize_database()

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🤖",
    layout="wide",
)

st.title("AI Project Manager, RAG And Model Evaluation")

st.markdown(
"""
### Models
1. **openai-gpt-oss-20b**
2. **Ollama-Llama 3.1 8B**
3. **Ollama-Qwen 2.5 7B Instruct**

For every question you can:
- run one model;
- or run the same question through all 3 models;
- see the answer;
- see the retrieved PDF page/chunk;
- open the PDF at the source page;
- see input/output/total tokens;
- compare models on the Dashboard.
"""
)
