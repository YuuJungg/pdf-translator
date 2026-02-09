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

    def extract_text_by_pages(self):
        if not self.doc:
            if not self.open_pdf():
                return []
        
        pages_content = []
        for page in self.doc:
            pages_content.append(page.get_text())
        
        return pages_content

    def extract_text(self):
        pages = self.extract_text_by_pages()
        return "\n--- PAGE BREAK ---\n".join(pages)

    def get_page_count(self):
        if not self.doc:
            self.open_pdf()
        return len(self.doc) if self.doc else 0

    def close(self):
        if self.doc:
            self.doc.close()
