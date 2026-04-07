import pdfplumber
import docx
import pytesseract
from PIL import Image
from services.advanced_parser import AdvancedResumeParser
from typing import Dict, Tuple


def parse_pdf(path):
    """Legacy PDF parsing function with word reconstruction fallback"""
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            if not page_text or len(page_text.strip()) < 50:
                try:
                    words = page.extract_words()
                    if words:
                        lines = []
                        current_line = []
                        last_top = None
                        for word in words:
                            if last_top is not None and abs(word["top"] - last_top) > 8:
                                lines.append(" ".join(current_line))
                                current_line = []
                            current_line.append(word["text"])
                            last_top = word["top"]
                        if current_line:
                            lines.append(" ".join(current_line))
                        page_text = "\n".join(lines)
                except Exception:
                    pass
            if not page_text or len(page_text.strip()) < 50:
                try:
                    page_image_obj = page.to_image(resolution=300)
                    pil_img = None
                    if hasattr(page_image_obj, 'original') and page_image_obj.original is not None:
                        pil_img = page_image_obj.original
                    elif hasattr(page_image_obj, 'image') and page_image_obj.image is not None:
                        pil_img = page_image_obj.image
                    elif hasattr(page_image_obj, 'render'):
                        pil_img = page_image_obj.render()
                    if pil_img is not None:
                        pil_img = pil_img.convert('RGB')
                        page_text = pytesseract.image_to_string(pil_img) or page_text
                except Exception:
                    pass
            text += page_text or ""
    return text


def parse_docx(path):
    """Legacy DOCX parsing function"""
    doc = docx.Document(path)
    return "\n".join([para.text for para in doc.paragraphs])


def parse_image(path):
    """Legacy image parsing function"""
    img = Image.open(path)
    try:
        return pytesseract.image_to_string(img)
    except Exception as e:
        print(f"Legacy image OCR failed: {e}")
        return ""


def extract_text(filepath):
    """
    Extract text from resume file (backward compatible)
    Automatically uses advanced parser for better results, with a fallback to legacy parsers when no text is found.
    """
    text = ""
    try:
        parser = AdvancedResumeParser()
        text = parser.get_full_text(filepath)
        if text and text.strip():
            return text
    except Exception as e:
        print(f"Advanced parser failed: {e}, falling back to basic parser")
    
    # Fallback to legacy parsing when advanced parser returned no text
    filepath_lower = filepath.lower()
    if filepath_lower.endswith(".pdf"):
        return parse_pdf(filepath)
    elif filepath_lower.endswith(".docx"):
        return parse_docx(filepath)
    elif filepath_lower.endswith((".png", ".jpg", ".jpeg")):
        return parse_image(filepath)
    return text or ""


def parse_resume_structured(filepath: str) -> Dict:
    """
    Parse resume and extract structured data including:
    - Contact information
    - Experience entries with dates
    - Education entries
    - Skills list
    - Detected sections
    - Metadata and extraction method
    """
    parser = AdvancedResumeParser()
    return parser.parse_resume(filepath)
