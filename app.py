import streamlit as st
import os

# Create a folder called 'uploads' if it doesn't exist
os.makedirs("uploads", exist_ok=True)


st.set_page_config(page_title="EzyHUB Research Agent", page_icon="🔍", layout="centered")

with st.sidebar:
    st.header("⚙️ Advanced Options")
    model_choice = st.selectbox("Choose model", ["Local LLM", "GPT-4", "Mix"])
    show_sources = st.checkbox("Show source notes")
    language = st.selectbox("Language", ["English", "Hindi", "Telugu", "Tamil"])

st.markdown("""
<div style='text-align: center;'>
    <a href='https://github.com/gudipatipreethi/ezyhub-agent' target='_blank'>
        <img src='ezyhub_logo.png' width='150'>
    </a>
</div>
""", unsafe_allow_html=True)

st.markdown("""
### 👋 Welcome to EzyHUB Research Agent

Upload your research notes, PDFs, or Word files. Ask questions in any language. Get clear, inclusive answers with source references.

**Use cases:**
- Client presentations
- Rural outreach
- Multilingual support
- Visual storytelling
""")


st.title("EzyHUB Research Agent")
st.markdown("Ask questions based on your research notes, PDFs, and URLs.")

uploaded_file = st.file_uploader("📎 Upload your research file", type=["pdf", "txt", "docx"])
if uploaded_file is not None:
    # Save the uploaded file permanently
    file_path = os.path.join("uploads", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"✅ File saved as: {uploaded_file.name}")

saved_files = os.listdir("uploads")
if saved_files:
    st.markdown("📂 **Saved Files:**")
    for file in saved_files:
        st.markdown(f"- {file}")

if uploaded_file is not None:
    file_text = uploaded_file.read().decode("utf-8", errors="ignore")
    st.text_area("📄 File Preview", file_text[:1000])  # Show first 1000 characters

# 🔍 Extract text from the uploaded file
if uploaded_file.name.endswith(".pdf"):
    from PyPDF2 import PdfReader
    reader = PdfReader(file_path)
    text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

elif uploaded_file.name.endswith(".docx"):
    from docx import Document
    doc = Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])

else:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

st.text_area("📄 File Preview", text[:1000])  # Optional preview

# 📝 Generate summary using LangChain
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms import OpenAI

summary_prompt = PromptTemplate.from_template("Summarize this document:\n{text}")
llm = OpenAI(openai_api_key="your-openai-key")  # Replace with your actual key
summary_chain = LLMChain(llm=llm, prompt=summary_prompt)
summary = summary_chain.run({"text": text})

st.markdown("📝 **Summary of the Document:**")
st.info(summary)

