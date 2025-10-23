import streamlit as st
import os
from PyPDF2 import PdfReader
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from deep_translator import GoogleTranslator

# Create uploads folder
os.makedirs("uploads", exist_ok=True)

# Page setup
st.set_page_config(page_title="EzyHUB Research Agent", page_icon="🔍", layout="wide")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    language = st.selectbox("Translate summary to", ["None", "Hindi", "Tamil", "Telugu"])
    download_choice = st.radio("⬇️ Download", ["None", "Summary only", "Full text + summary"])
    search_term = st.text_input("🔎 Search in saved files")
    all_files = os.listdir("uploads")
    filtered_files = [f for f in all_files if search_term.lower() in f.lower()] if search_term else all_files
    selected_file = st.selectbox("📂 View saved file", ["None"] + filtered_files)

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

        # Translation
        if language != "None":
            lang_map = {"Hindi": "hi", "Tamil": "ta", "Telugu": "te"}
            try:
                translated = GoogleTranslator(source='auto', target=lang_map[language]).translate(summary)
                st.markdown(f"🌐 **Translated Summary ({language}):**")
                st.success(translated)
            except Exception as e:
                st.warning("⚠️ Translation failed. Please check your internet or try again.")

        # Download
        if download_choice == "Summary only":
            st.download_button("⬇️ Download Summary", summary, file_name="summary.txt")
        elif download_choice == "Full text + summary":
            full_export = f"Summary:\n{summary}\n\nFull Text:\n{text}"
            st.download_button("⬇️ Download Full Text + Summary", full_export, file_name="full_text_summary.txt")

    except Exception as e:
        st.warning("⚠️ Could not generate summary. Try a simpler file.")

else:
    st.info("📂 Select a saved file from the sidebar to preview and summarize.")