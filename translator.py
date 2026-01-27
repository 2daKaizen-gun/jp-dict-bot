import os
import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv

# 환경 변수 로드 및 API 설정
load_dotenv()
# 로컬 환경 변수가 없으면 Streamlit Secrets에서 가져오도록 설정 (배포 대비)
def initialize_gemini():
    api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found. Please set it in your environment variables or Streamlit Secrets")
    genai.configure(api_key=api_key)

# 초기화 실행
initialize_gemini()

def get_raw_response_from_gemini(word, target_level, database_id):
    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        
        # Detect Language Mode
        my_id = os.getenv("NOTION_DATABASE_ID") or st.secrets.get("NOTION_DATABASE_ID")
        korean_mode = (database_id == my_id)
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

        response = model.generate_content(prompt)
        return response.text if response.text else None
    
    except Exception as e:
        st.error(f"Gemini Analysis Error: {e}")
        return None