import streamlit as st
import os
from PyPDF2 import PdfReader
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# Create uploads folder
os.makedirs("uploads", exist_ok=True)

# Page setup
st.set_page_config(page_title="EzyHUB Research Agent", page_icon="🔍", layout="wide")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    model_choice = st.selectbox("Choose model", ["Local (free)", "GPT-4 (premium)", "Mix"])
    language = st.selectbox("Language", ["English", "Hindi", "Telugu", "Tamil"])
    font_size = st.slider("🔠 Font size", 12, 24, 16)
    translate_summary = st.checkbox("🌐 Translate summary")
    download_choice = st.radio("⬇️ Download", ["None", "Summary only", "Full text + summary"])
    search_term = st.text_input("🔎 Search in saved files")

    # Filter saved files
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
st.markdown("Upload your research file, preview its contents, and get a quick summary.")

# Upload new file
uploaded_file = st.file_uploader("📎 Upload a new research file", type=["pdf", "txt", "docx"])
if uploaded_file:
    file_name = uploaded_file.name
    file_path = os.path.join("uploads", file_name)

    # Save permanently
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"✅ File saved as: {file_name}")
    selected_file = file_name  # auto-select after upload

# Load selected file
if selected_file and selected_file != "None":
    file_path = os.path.join("uploads", selected_file)

    # Extract text
    if selected_file.endswith(".pdf"):
        reader = PdfReader(file_path)
        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif selected_file.endswith(".docx"):
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
    else:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

    # Preview
    with st.expander("📄 File Preview"):
        st.text_area("Preview", text[:1000], height=300)

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

        # Optional translation placeholder
        if translate_summary:
            st.markdown("🌐 Translated Summary (Coming Soon)")
            st.write("Translation into Kannada, Tamil, Telugu will appear here.")

        # Optional download placeholder
        if download_choice != "None":
            st.markdown("⬇️ Download option selected (Coming Soon)")
            st.write(f"You chose: {download_choice}. Download buttons will appear here.")

    except Exception as e:
        st.warning("⚠️ Could not generate summary. Try a simpler file.")

else:
    st.info("📂 Select a saved file from the sidebar to preview and summarize.")