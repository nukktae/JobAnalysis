from PyPDF2 import PdfReader
import io

def extract_text_from_pdf(pdf_file):
    try:
        # Create a PDF reader object
        pdf_reader = PdfReader(io.BytesIO(pdf_file.read()))
        
        # Extract text from all pages
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
            
        if not text.strip():
            raise Exception("No text could be extracted from the PDF")
            
        return text.strip()
        
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}") 