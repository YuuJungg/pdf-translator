from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self, api_key=None, model_name=None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API Key is required.")

        self.client = genai.Client(api_key=self.api_key)

        # ✅ 기본 모델 하드코딩 지양: 가능하면 자동 선택
        self.default_model = model_name or self._pick_default_model()

    def _pick_default_model(self) -> str:
        """
        현재 API에서 사용 가능한 모델 중
        generateContent 지원하는 모델만 추려서
        Flash 우선 → Pro 차선으로 선택
        """
        try:
            models = list(self.client.models.list())

            # generateContent 지원 모델만
            candidates = []
            for m in models:
                name = getattr(m, "name", "") or ""
                methods = getattr(m, "supported_generation_methods", None) or []
                if "generateContent" in methods and "gemini" in name.lower():
                    # Strip 'models/' prefix if present
                    clean_name = name.replace("models/", "")
                    candidates.append(clean_name)

            if not candidates:
                return "gemini-1.5-flash" # Safe fallback

            # 선호도: flash 계열 우선, 그 다음 pro
            preferred_keywords = ["flash", "pro"]
            for kw in preferred_keywords:
                for name in candidates:
                    if kw in name.lower():
                        return name

            # 그래도 없으면 첫 번째
            return candidates[0]
        except:
            return "gemini-1.5-flash" # Final safety net

    def _generate_with_fallback(self, prompt: str) -> str:
        # ✅ 후보를 “가볍게”만 두고, 1순위는 자동 선택된 default_model
        model_candidates = [
            self.default_model,
            "gemini-1.5-flash",
            "gemini-1.5-pro",
        ]

        last_error = None
        for model_name in model_candidates:
            if not model_name:
                continue
            try:
                resp = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                return resp.text
            except Exception as e:
                last_error = e
                msg = str(e).lower()

                # 권한 문제면 즉시 종료
                if "403" in msg or "permission_denied" in msg:
                    raise

                # 모델명/지원메서드 문제면 다음 후보로
                if "404" in msg or "not found" in msg or "supported" in msg:
                    continue

                # 그 외(네트워크 등)는 바로 터뜨리기
                raise

        raise last_error or RuntimeError("No valid models found to process the request.")

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
        return self._generate_with_fallback(prompt)

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
        return self._generate_with_fallback(prompt)
