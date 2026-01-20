import os
import google.generativeai as genai
from dotenv import load_dotenv
import json

# 1. 환경 변수 로드 및 API 설정
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def fetch_vocabulary_data(word):
    """
    Gemini API를 사용하여 한국어 단어에 대한 
    일본어 번역 및 학습 데이터를 추출하는 함수
    """
    model = genai.GenerativeModel('gemini-flash-latest')
    
  # 더 구체적이고 전문적인 지시사항 (System Instruction)
    prompt = f"""
    Act as a professional Japanese language instructor and IT career consultant for Korean students.
    Your task is to provide learning data for the Korean word '{word}'.
    
    Return the result ONLY in JSON format with these exact keys:
    - word: Japanese Kanji (or Hiragana if no Kanji is commonly used).
    - furigana: Hiragana reading.
    - meaning: Korean translation.
    - level: JLPT level (N1~N5).
    - example_ja: A natural Japanese sentence. Prioritize business or IT-related contexts if possible.
    - example_ko: Korean translation of the example.
    - nuance: A short tip (in Korean) about the word's nuance or usage in Japan (e.g., 'Used in formal situations').

    CRITICAL: Output MUST be a valid JSON object. No markdown, no backticks, no extra text.
    """

    try:
        response = model.generate_content(prompt)
        # JSON 문자열만 추출하기 위한 정규화
        content = response.text.strip()
        if content.startswith("```json"):
            content = content.split("```json")[1].split("```")[0].strip()
        elif content.startswith("```"):
            content = content.split("```")[1].split("```")[0].strip()
            
        data = json.loads(content)
        return data
    except Exception as e:
        print(f"Error: {e}")
        return None

# 테스트 실행
if __name__ == "__main__":
    test_word = "결심"
    result = fetch_vocabulary_data(test_word)
    if result:
        print(json.dumps(result, indent=4, ensure_ascii=False))