import fitz  # PyMuPDF
import os

class PDFProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.doc = None

    def open_pdf(self):
        try:
            self.doc = fitz.open(self.file_path)
            return True
        except Exception as e:
            print(f"Error opening PDF: {e}")
            return False

    def extract_text(self):
        if not self.doc:
            if not self.open_pdf():
                return ""
        
        full_text = ""
        for page in self.doc:
            full_text += page.get_text() + "\n--- PAGE BREAK ---\n"
        
        return full_text

    def get_page_count(self):
        if not self.doc:
            self.open_pdf()
        return len(self.doc) if self.doc else 0

    def close(self):
        if self.doc:
            self.doc.close()
