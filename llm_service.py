import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API Key is required.")
        self.genai = genai
        self.genai.configure(api_key=self.api_key)
        # Default model
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def translate_text(self, text):
        prompt = f"""
        Role: Senior Liaison Interpreter & Technical Translator
        Task: Translate the following English academic/technical text into clear, academic, and natural Korean.
        
        Guidelines:
        1. Accuracy: Do not omit or change the meaning.
        2. Context: Maintain the formal tone and professional style of the original.
        3. Terminology: Use standard academic Korean terminology. For highly specific terms, keep the English in brackets (e.g., "Term(원어)").
        4. Markdown: Preserve any markdown formatting.
        5. Length: This is a large text, ensure consistency across the entire document.

        Text to Translate:
        {text}
        """
        response = self.model.generate_content(prompt)
        return response.text

    def summarize_text(self, text):
        prompt = f"""
        Role: Executive Researcher and Strategist
        Task: Provide a high-level executive summary of the following document in Korean.
        
        Guidelines:
        1. Context: Understand the core thesis, methodology, and conclusion.
        2. Format: Use professional bullet points and sections.
        3. Depth: Provide enough detail to understand the core contribution without reading the full text.
        4. Language: Korean.

        Document Content:
        {text}
        """
        response = self.model.generate_content(prompt)
        return response.text

    def process_large_document(self, text, task_type="translate"):
        # Large context support (Gemini 1.5 supports up to 1M+ tokens)
        # For extremely large files, we might still need chunking, 
        # but for 100-200 pages, we can try larger chunks or single pass if it fits.
        # Here we'll implement a simple split logic if token count is very high.
        
        if task_type == "translate":
            return self.translate_text(text)
        else:
            return self.summarize_text(text)
