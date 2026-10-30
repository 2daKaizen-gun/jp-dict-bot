from google import genai
from google.genai import types
import streamlit as st
from config import get_secret, is_personal_db

MODEL_NAME = "gemini-flash-latest"

# 로컬 환경 변수가 없으면 Streamlit Secrets에서 가져오도록 설정 (배포 대비)
def initialize_gemini():
    api_key = get_secret("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found. Please set it in your environment variables or Streamlit Secrets")
    return genai.Client(api_key=api_key)

# 초기화 실행
client = initialize_gemini()

def get_raw_response_from_gemini(word, target_level, database_id):
    try:
        # Detect Language Mode
        korean_mode = is_personal_db(database_id)
        response_lang = "Korean" if korean_mode else "English"

        # 레벨에 따른 추가 지시문 생성
        level_instruction = ""
        if target_level != "Auto-detect":
            level_instruction = f"The user is currently studying for JLPT {target_level}. Please provide an example sentence and nuance explanation optimized for the {target_level} level."
        else:
            level_instruction = "Analyze the word's typical difficulty and assign a JLPT level (N1~N5) naturally."

        # 전문적인 지시사항 (System Instruction)
        prompt = f"""
        You are a professional Japanese linguist and career consultant.
        Analyze the word: '{word}' and provide linguistic insights.

        [Target Audience]
        - Proficiency: {level_instruction}
        - Explanation Language: **{response_lang}**

        [Output Format]
        Return ONLY a raw JSON object with these exact keys:
        - word: The Japanese expression (Kanji/Hiragana).
        - furigana: The reading in Hiragana.
        - meaning: Concise translation in **{response_lang}**.
        - level: JLPT level (N1-N5).
        - example_ja: A natural Japanese sentence (Business/IT context preferred).
        - example: Accurate translation of example_ja in **{response_lang}**.
        - nuance: 1-2 sentences explaining the usage/tone in **{response_lang}**.

        CRITICAL: No markdown backticks, no conversational text. Return only the JSON string.
        """

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            # JSON 형식 응답 강제 (파서는 방어용으로 유지)
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return response.text if response.text else None
    
    except Exception as e:
        st.error(f"Gemini Analysis Error: {e}")
        return None