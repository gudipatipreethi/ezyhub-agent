import streamlit as st
import os
from PyPDF2 import PdfReader
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# Create uploads folder if it doesn't exist
os.makedirs("uploads", exist_ok=True)

st.set_page_config(page_title="EzyHUB Research Agent", page_icon="🔍", layout="centered")

st.title("EzyHUB Research Agent")
st.markdown("Upload your research file and get a quick summary.")

# Upload file
uploaded_file = st.file_uploader("📎 Upload your research file", type=["pdf", "txt", "docx"])
if uploaded_file is not None:
    file_name = uploaded_file.name
    file_path = os.path.join("uploads", file_name)

    # Save file permanently
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"✅ File saved permanently as: {file_name}")

    # Extract text
    if file_name.endswith(".pdf"):
        reader = PdfReader(file_path)
        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif file_name.endswith(".docx"):
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
    else:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

    # Preview text
    st.text_area("📄 File Preview", text[:1000])

    # Generate basic summary using TF-IDF + KMeans
    st.markdown("📝 **Summary of the Document:**")
    try:
        sentences = text.split(". ")
        vectorizer = TfidfVectorizer(stop_words="english")
        X = vectorizer.fit_transform(sentences)
        kmeans = KMeans(n_clusters=1, random_state=42).fit(X)
        summary_sentences = [sentences[i] for i in range(len(sentences)) if kmeans.labels_[i] == 0]
        summary = " ".join(summary_sentences[:5])
        st.info(summary)
    except Exception as e:
        st.warning("⚠️ Could not generate summary. Try a simpler file.")

# Show saved files
saved_files = os.listdir("uploads")
if saved_files:
    st.markdown("📂 **Saved Files:**")
    for file in saved_files:
        st.markdown(f"- {file}")