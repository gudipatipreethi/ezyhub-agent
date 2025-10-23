import streamlit as st
import os
from PyPDF2 import PdfReader
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer
import faiss
from deep_translator import GoogleTranslator
from ctransformers import AutoModelForCausalLM

# Setup
os.makedirs("uploads", exist_ok=True)
st.set_page_config(page_title="EzyHUB Research Agent", page_icon="🔍", layout="wide")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    model_choice = st.selectbox("Choose model", ["Local LLM", "GPT-4 (premium)", "Mix"])
    language = st.selectbox("Language", ["English", "Hindi", "Telugu", "Tamil"])
    font_size = st.slider("🔠 Font size", 12, 24, 16)
    translate_summary = st.checkbox("🌐 Translate summary")
    download_choice = st.radio("⬇️ Download", ["None", "Summary only", "Full text + summary"])
    search_term = st.text_input("🔎 Search in saved files")
    all_files = os.listdir("uploads")
    filtered_files = [f for f in all_files if search_term.lower() in f.lower()] if search_term else all_files
    selected_file = st.selectbox("📂 View saved file", ["None"] + filtered_files)

# Header
st.markdown(f"""
<div style='text-align: center; font-size:{font_size}px'>
    <a href='https://github.com/gudipatipreethi/ezyhub-agent' target='_blank'>
        <img src='ezyhub_logo.png' width='150'>
    </a>
</div>
""", unsafe_allow_html=True)

st.title("EzyHUB Research Agent")
st.markdown("Upload your research file, preview its contents, ask questions, and get a quick summary.")

# Upload
uploaded_file = st.file_uploader("📎 Upload a new research file", type=["pdf", "txt", "docx"])
if uploaded_file:
    file_name = uploaded_file.name
    file_path = os.path.join("uploads", file_name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"✅ File saved as: {file_name}")
    selected_file = file_name

# Load and extract
text = ""
if selected_file and selected_file != "None":
    file_path = os.path.join("uploads", selected_file)
    if selected_file.endswith(".pdf"):
        reader = PdfReader(file_path)
        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif selected_file.endswith(".docx"):
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
    else:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

    st.text_area("📄 File Preview", text[:1000], height=300)

    # Summary
    st.markdown("📝 **Summary of the Document:**")
    try:
        sentences = text.split(". ")
        vectorizer = TfidfVectorizer(stop_words="english")
        X = vectorizer.fit_transform(sentences)
        kmeans = KMeans(n_clusters=1, random_state=42).fit(X)
        summary_sentences = [sentences[i] for i in range(len(sentences)) if kmeans.labels_[i] == 0]
        summary = " ".join(summary_sentences[:5])
        st.info(summary)

        if translate_summary:
            st.markdown("🌐 Translated Summary:")
            try:
                lang_map = {"Hindi": "hi", "Tamil": "ta", "Telugu": "te"}
                if language in lang_map:
                    translated = GoogleTranslator(source='auto', target=lang_map[language]).translate(summary)
                    st.success(translated)
                else:
                    st.info("No translation needed for English.")
            except Exception as e:
                st.warning("⚠️ Translation failed.")

        if download_choice == "Summary only":
            st.download_button("⬇️ Download Summary", summary, file_name="summary.txt")
        elif download_choice == "Full text + summary":
            full_export = f"Summary:\n{summary}\n\nFull Text:\n{text}"
            st.download_button("⬇️ Download Full Text + Summary", full_export, file_name="full_text_summary.txt")

    except Exception as e:
        st.warning("⚠️ Could not generate summary.")

    # RAG setup
    model = SentenceTransformer("all-MiniLM-L6-v2")
    chunks = [text[i:i+500] for i in range(0, len(text), 500)]
    embeddings = model.encode(chunks)
    index = faiss.IndexFlatL2(len(embeddings[0]))
    index.add(embeddings)

    # Load local LLM
    try:
        llm = AutoModelForCausalLM.from_pretrained(
            "TheBloke/Mistral-7B-Instruct-v0.1-GGUF",
            model_file="mistral-7b-instruct-v0.1.Q4_K_M.gguf",
            model_type="mistral"
        )
    except Exception as e:
        llm = None
        st.warning("⚠️ Local LLM not loaded. Check model path or install.")

    # File-specific chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = {}
    if selected_file not in st.session_state.chat_history:
        st.session_state.chat_history[selected_file] = []

    # Chat interface
    user_input = st.chat_input("Ask a question about your document")
    if user_input:
        st.session_state.chat_history[selected_file].append(("user", user_input))
        question_embedding = model.encode([user_input])
        _, I = index.search(question_embedding, k=3)
        context = "\n".join([chunks[i] for i in I[0]])
        prompt = f"Answer the question based on the context below.\n\nContext:\n{context}\n\nQuestion: {user_input}\nAnswer:"
        if llm:
            response = llm(prompt)
        else:
            response = f"(LLM unavailable) Based on your document:\n\n{context[:500]}..."
        st.session_state.chat_history[selected_file].append(("assistant", response))

    for role, msg in st.session_state.chat_history[selected_file]:
        with st.chat_message(role):
            st.write(msg)

else:
    st.info("📂 Select a saved file from the sidebar to preview and chat.")