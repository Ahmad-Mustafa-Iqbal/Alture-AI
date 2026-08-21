import io
import re
from typing import Dict, Any

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract full text from PDF binary stream using pypdf."""
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        return "\n".join(text_parts).strip()
    except Exception as e:
        print(f"  [WARN] PDF extraction error: {e}")
        return ""

def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from Word .docx binary stream using python-docx."""
    try:
        import docx
        doc = docx.Document(io.BytesIO(file_bytes))
        full_text = []
        for para in doc.paragraphs:
            if para.text.strip():
                full_text.append(para.text)
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        full_text.append(cell.text)
        return "\n".join(full_text).strip()
    except Exception as e:
        print(f"  [WARN] DOCX extraction error: {e}")
        return ""

def extract_text_from_txt(file_bytes: bytes) -> str:
    """Extract text from TXT file bytes with utf-8 / latin-1 fallback."""
    try:
        return file_bytes.decode('utf-8').strip()
    except UnicodeDecodeError:
        return file_bytes.decode('latin-1', errors='ignore').strip()

def parse_resume_file(filename: str, file_bytes: bytes) -> Dict[str, Any]:
    """
    Unified parser extracting text and candidate metadata from PDF, DOCX, or TXT resumes.
    """
    ext = filename.lower().split('.')[-1]
    
    if ext == 'pdf':
        text = extract_text_from_pdf(file_bytes)
    elif ext in ['docx', 'doc']:
        text = extract_text_from_docx(file_bytes)
    elif ext in ['txt', 'md', 'rtf']:
        text = extract_text_from_txt(file_bytes)
    else:
        # Fallback to text decoding
        text = extract_text_from_txt(file_bytes)

    # Clean whitespace
    clean_text = re.sub(r'[ \t]+', ' ', text)
    clean_text = re.sub(r'\n{3,}', '\n\n', clean_text).strip()
    
    words = re.findall(r'\w+', clean_text)
    word_count = len(words)

    # Heuristic for Candidate Name (First non-empty line without labels)
    candidate_name = "Candidate"
    lines = [line.strip() for line in clean_text.split('\n') if line.strip()]
    for line in lines[:3]:
        # Filter out common headers
        if not re.search(r'resume|curriculum|vitae|summary|experience|education|contact|phone|email|profile', line, re.IGNORECASE):
            if len(line.split()) <= 4 and len(line) <= 40:
                candidate_name = line.replace('|', '').strip()
                break

    # Email heuristic
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', clean_text)
    email = email_match.group(0) if email_match else None

    return {
        "status": "success" if word_count > 15 else "warning",
        "filename": filename,
        "candidate_name": candidate_name,
        "email": email,
        "word_count": word_count,
        "extracted_text": clean_text
    }
