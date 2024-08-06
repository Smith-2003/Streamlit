import streamlit as st
from PyPDF2 import PdfReader
from io import BytesIO
from docx import Document

st.set_page_config(page_title="PDF Text Extractor", page_icon="📄", layout="wide")

st.title("PDF Text Extractor with OCR")
st.markdown("""
<style>
.container {
    padding: 2rem;
    background-color: #f9f9f9;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}
.download-btn {
    background-color: #4CAF50;
    color: white;
    padding: 10px 20px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    border-radius: 5px;
    margin: 10px 2px;
    cursor: pointer;
}
.download-btn:hover {
    background-color: #45a049;
}
</style>
""", unsafe_allow_html=True)

uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)

if uploaded_files:
    all_texts = ""
    for uploaded_file in uploaded_files:
        with st.spinner(f"Extracting text from {uploaded_file.name}..."):
            pdf_reader = PdfReader(uploaded_file)
            extracted_text = ""

            # Iterate through each page and extract text
            for page_number, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                extracted_text += f"\n\n--- Page {page_number + 1} ---\n\n{text}"

            all_texts += f"\n\n--- Document: {uploaded_file.name} ---\n\n{extracted_text}"
    
    st.markdown('<div class="container"><h2>Extracted Text</h2></div>', unsafe_allow_html=True)
    st.text_area("", all_texts, height=400)

    def save_text_as_file(file_type):
        if file_type == "txt":
            b = BytesIO()
            b.write(all_texts.encode())
            b.seek(0)
            return b, "extracted_text.txt"
        elif file_type == "docx":
            doc = Document()
            doc.add_paragraph(all_texts)
            b = BytesIO()
            doc.save(b)
            b.seek(0)
            return b, "extracted_text.docx"

    b_txt, filename_txt = save_text_as_file("txt")
    b_docx, filename_docx = save_text_as_file("docx")

    st.download_button("Download .txt", data=b_txt, file_name=filename_txt)
    st.download_button("Download .docx", data=b_docx, file_name=filename_docx)