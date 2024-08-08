import streamlit as st
from PyPDF2 import PdfReader
from io import BytesIO
from docx import Document
from PIL import Image, ExifTags
import pytesseract
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()



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

pdfuploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)

if pdfuploaded_files:
    all_texts = ""
    for uploaded_file in pdfuploaded_files:
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
        

# Get the Tesseract path from the environment variable
TESSERACT_PATH = os.getenv('TESSERACT_PATH')

# Set the path for Tesseract executable
if TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = os.path.join(TESSERACT_PATH, 'tesseract.exe')
else:
    st.error("TESSERACT_PATH environment variable is not set.")
    st.stop()

    # Function to correct image orientation based on EXIF data
def correct_image_orientation(image):
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = image._getexif()
        if exif is not None:
            orientation_value = exif.get(orientation)
            if orientation_value == 3:
                image = image.rotate(180, expand=True)
            elif orientation_value == 6:
                image = image.rotate(270, expand=True)
            elif orientation_value == 8:
                image = image.rotate(90, expand=True)
    except Exception as e:
        st.warning("Could not correct image orientation: " + str(e))
    return image
# Create a folder to store the uploaded images
if not os.path.exists("uploaded_images"):
    os.makedirs("uploaded_images")

# Create a folder to store the extracted text files
extracted_text_dir = "extracted_text"
if not os.path.exists(extracted_text_dir):
    os.makedirs(extracted_text_dir)

# Add a file uploader to the app that allows multiple file uploads
uploaded_files = st.file_uploader("Choose image files", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Check if files have been uploaded
if uploaded_files:
    for uploaded_file in uploaded_files:
        # Convert the uploaded file to an image
        image = Image.open(uploaded_file)

        # Correct the image orientation
        image = correct_image_orientation(image)

        # Get the file name
        file_name = uploaded_file.name
        
        # Save the image to the "uploaded_images" folder
        image.save(os.path.join("uploaded_images", file_name))
        
        # Display a success message
        st.success(f"Image '{file_name}' has been uploaded and saved to the 'uploaded_images' folder.")
        
        # Perform OCR on the image
        extracted_text = pytesseract.image_to_string(image)
        
        # Save the extracted text to a file
        text_file_name = os.path.splitext(file_name)[0] + ".txt"
        text_file_path = os.path.join(extracted_text_dir, text_file_name)
        
        with open(text_file_path, "w", encoding="utf-8") as text_file:
            text_file.write(extracted_text)
        
        # Display a success message for text file creation
        st.success(f"Extracted text has been saved to '{os.path.basename(text_file_path)}'.")

        # Add a download button for the extracted text file
        with open(text_file_path, "r", encoding="utf-8") as text_file:
            st.download_button(
                label="Download Extracted Text",
                data=text_file,
                file_name=text_file_name,
                mime="text/plain"
            )
