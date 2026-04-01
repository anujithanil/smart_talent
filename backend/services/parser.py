import pdfplumber
import docx
import pytesseract
from PIL import Image

def parse_pdf(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def parse_docx(path):
    doc = docx.Document(path)
    return "\n".join([para.text for para in doc.paragraphs])

def parse_image(path):
    img = Image.open(path)
    return pytesseract.image_to_string(img)

def extract_text(filepath):
    if filepath.endswith(".pdf"):
        return parse_pdf(filepath)
    elif filepath.endswith(".docx"):
        return parse_docx(filepath)
    elif filepath.endswith((".png", ".jpg", ".jpeg")):
        return parse_image(filepath)
    return ""