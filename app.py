import streamlit as st



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

if uploaded_file:
    st.success(f"Uploaded: {uploaded_file.name}")
    with st.expander("📄 File Preview"):
        file_text = uploaded_file.read().decode("utf-8", errors="ignore")
        st.text(file_text[:1000])  # Show first 1000 characters

query = st.text_input("🔍 Enter your question:")

if query:
    # Replace this with your actual function that connects to FAISS + local LLM
    def ask_research_agent(question):
        return "This is a placeholder answer. Replace with your real function."

    answer = ask_research_agent(query)
    st.markdown("### 🧠 Answer")
    st.write(answer)
