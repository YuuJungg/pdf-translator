from google import genai
import os
from dotenv import load_dotenv
import time

load_dotenv()

class LLMService:
    def __init__(self, api_key=None, model_name=None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API Key is required.")

        self.client = genai.Client(api_key=self.api_key)
        
        # ✅ Try to pick the best model dynamically, or use a provided hint
        self.default_model = model_name or self._pick_default_model()
        print(f"DEBUG: Initialized with model: {self.default_model}")

    def _pick_default_model(self) -> str:
        """
        현재 API 키로 접근 가능한 최적의 모델을 동적으로 탐색합니다.
        Flash 우선 -> Pro 차선
        """
        try:
            models = list(self.client.models.list())
            
            # generateContent를 지원하는 Gemini 모델만 필터링
            candidates = []
            for m in models:
                name = m.name # This is usually 'models/gemini-...'
                methods = m.supported_generation_methods or []
                if "generateContent" in methods and "gemini" in name.lower():
                    candidates.append(name)

            if not candidates:
                # 최후의 보루: 가장 널리 쓰이는 이름 시도
                return "gemini-1.5-flash-latest"

            # 1순위: Flash (속도와 비용 면에서 유리)
            for kw in ["flash-latest", "flash-002", "flash"]:
                for name in candidates:
                    if kw in name.lower():
                        return name
            
            # 2순위: Pro (정밀도)
            for kw in ["pro-latest", "pro-002", "pro"]:
                for name in candidates:
                    if kw in name.lower():
                        return name

            return candidates[0]
        except Exception as e:
            print(f"DEBUG: Model auto-discovery failed: {e}")
            return "gemini-1.5-flash-latest"

    def _generate_with_fallback(self, prompt: str) -> str:
        """
        여러 모델 후보를 순차적으로 시도하며 404 에러를 방지합니다.
        """
        # 후보군 구성 (최신 별칭 우선)
        model_candidates = [
            self.default_model,
            "gemini-1.5-flash-latest",
            "gemini-1.5-pro-latest",
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-2.0-flash-exp" # 최신 실험버전 시도
        ]

        # 중복 제거 (순서 유지)
        seen = set()
        unique_candidates = []
        for m in model_candidates:
            if m and m not in seen:
                unique_candidates.append(m)
                seen.add(m)

        last_error = None
        for model_name in unique_candidates:
            try:
                resp = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if not resp.text:
                    continue
                return resp.text
            except Exception as e:
                last_error = e
                msg = str(e).lower()
                
                # 심각한 권한 문제면 즉시 중단
                if "403" in msg or "permission_denied" in msg:
                    raise e
                
                # 404나 지원하지 않는 모델 에러일 경우에만 다음으로 넘어감
                if any(err in msg for err in ["404", "not_found", "not supported", "not found"]):
                    print(f"DEBUG: Model {model_name} failed with 404, trying next...")
                    continue
                
                # 할당량 초과(429) 시 잠시 대기 후 시도할 수도 있지만, 여기서는 다음 모델 시도
                if "429" in msg or "quota" in msg:
                    time.sleep(1)
                    continue

                # 기타 심각한 에러는 바로 터뜨림
                raise e

        # 모든 모델 실패 시 마지막 에러 보고
        error_info = f"All model attempts failed. Last error: {last_error}"
        raise RuntimeError(error_info)

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
