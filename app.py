import streamlit as st
import os
from PyPDF2 import PdfReader
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from deep_translator import GoogleTranslator

# Create uploads folder
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Page setup
st.set_page_config(page_title="EzyHUB Research Agent", page_icon="🔍", layout="wide")

# Initialize session state for selected file
if "selected_file" not in st.session_state:
    st.session_state.selected_file = "None"

# Sidebar settings
with st.sidebar:
    st.header("⚙️ Settings")
    language = st.selectbox("Translate summary to", ["None", "Hindi", "Tamil", "Telugu"])
    download_choice = st.radio("⬇️ Download", ["None", "Summary only", "Full text + summary"])
    search_term = st.text_input("🔎 Search in saved files")

    # Refresh file list
    all_files = os.listdir(UPLOAD_DIR)
    filtered_files = [f for f in all_files if search_term.lower() in f.lower()] if search_term else all_files

    # File selector
    selected = st.selectbox("📂 View saved file", ["None"] + filtered_files, index=filtered_files.index(st.session_state.selected_file) + 1 if st.session_state.selected_file in filtered_files else 0)
    st.session_state.selected_file = selected

# Upload new file
uploaded_file = st.file_uploader("📎 Upload a new research file", type=["pdf", "txt", "docx"])
if uploaded_file:
    file_name = uploaded_file.name
    file_path = os.path.join(UPLOAD_DIR, file_name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"✅ File saved as: {file_name}")
    st.session_state.selected_file = file_name  # auto-select after upload
    st.experimental_rerun()  # refresh to update sidebar

# Load and extract text
text = ""
if st.session_state.selected_file and st.session_state.selected_file != "None":
    file_path = os.path.join(UPLOAD_DIR, st.session_state.selected_file)
    try:
        if st.session_state.selected_file.endswith(".pdf"):
            reader = PdfReader(file_path)
            text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        elif st.session_state.selected_file.endswith(".docx"):
            doc = Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
        elif st.session_state.selected_file.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        else:
            st.warning("Unsupported file type.")
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")

    if text:
        st.text_area("📄 File Preview", text[:1000], height=300)

        # Generate summary
        st.markdown("📝 **Summary of the Document:**")
        try:
            sentences = [s.strip() for s in text.split(". ") if len(s.strip()) > 20]
            if len(sentences) < 2:
                raise ValueError("Not enough content to summarize.")
            vectorizer = TfidfVectorizer(stop_words="english")
            X = vectorizer.fit_transform(sentences)
            kmeans = KMeans(n_clusters=1, random_state=42).fit(X)
            summary_sentences = [sentences[i] for i in range(len(sentences)) if kmeans.labels_[i] == 0]
            summary = " ".join(summary_sentences[:5])
            st.info(summary)

            # Translate summary
            if language != "None":
                lang_map = {"Hindi": "hi", "Tamil": "ta", "Telugu": "te"}
                try:
                    translated = GoogleTranslator(source='auto', target=lang_map[language]).translate(summary)
                    st.markdown(f"🌐 **Translated Summary ({language}):**")
                    st.success(translated)
                except Exception as e:
                    st.warning("⚠️ Translation failed. Please check your internet or try again.")

            # Download options
            if download_choice == "Summary only":
                st.download_button("⬇️ Download Summary", summary, file_name="summary.txt")
            elif download_choice == "Full text + summary":
                full_export = f"Summary:\n{summary}\n\nFull Text:\n{text}"
                st.download_button("⬇️ Download Full Text + Summary", full_export, file_name="full_text_summary.txt")

        except Exception as e:
            st.warning("⚠️ Could not generate summary. Try a simpler file.")
else:
    st.info("📂 Select a saved file from the sidebar to preview and summarize.")