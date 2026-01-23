import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. 환경 변수 로드 및 API 설정
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_raw_response_from_gemini(word):
    model = genai.GenerativeModel('gemini-flash-latest')
  # 전문적인 지시사항 (System Instruction)
    prompt = f"'{word}'에 대한 학습 데이터를 JSON 형식으로 알려줘.."""""
    Act as a professional Japanese language instructor and IT career consultant for Korean students.
    Your task is to provide learning data for the Korean word '{word}'.
    
    Return the result ONLY in JSON format with these exact keys:
    - word: Japanese Kanji (or Hiragana if no Kanji is commonly used).
    - furigana: Hiragana reading.
    - meaning: Korean translation.
    - level: JLPT level (N1~N5).
    - example_ja: A natural Japanese short sentence. Prioritize business or IT-related contexts if possible. 
    - example_ko: Korean translation of the example.
    - nuance: A short tip (in Korean, using 1 or 2 sentences) about the word's nuance or usage in Japan (e.g., 'Used in formal situations').

    CRITICAL: Output MUST be a valid JSON object. No markdown, no backticks, no extra text.
    """

    response = model.generate_content(prompt)
    return response.text # 정제하지 않은 문자열 그대로 반환