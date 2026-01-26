import os
import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv

# 환경 변수 로드 및 API 설정
load_dotenv()
# [보안 팁] 로컬 환경 변수가 없으면 Streamlit Secrets에서 가져오도록 설정 (배포 대비)
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

def get_raw_response_from_gemini(word, target_level):
    model = genai.GenerativeModel('gemini-flash-latest')
    
    # 레벨에 따른 추가 지시문 생성
    level_instruction = ""
    if target_level != "자동 판정":
        level_instruction = f"The user is currently studying for JLPT {target_level}. Please provide an example sentence and nuance explanation optimized for the {target_level} level."
    else:
        level_instruction = "Analyze the word's typical difficulty and assign a JLPT level (N1~N5) naturally."

    # 전문적인 지시사항 (System Instruction)
    prompt = f"""
    You are a professional Japanese linguist and IT career consultant for students.
    Analyze the word: '{word}' (regardless of its source language: Korean, English, etc.)
    and provide the most accurate Japanese translation and context.

    {level_instruction}

    Return the result ONLY in JSON format with these exact keys:
    - word: Japanese Kanji (or Hiragana if no Kanji is commonly used).
    - furigana: Hiragana reading.
    - meaning: Korean translation.
    - level: JLPT level (N1~N5).
    - example_ja: A natural Japanese short sentence. Prioritize business or IT-related contexts if possible. 
    - example_ko: Korean translation of the example.
    - nuance: A short tip (in Korean, using 1 or 2 sentences) about the word's nuance or usage in Japan.

    CRITICAL: Output MUST be a valid JSON object. No markdown, no backticks, no extra text.
    Do not include any conversational text, markdown code blocks, or explanations outside the JSON.
    """

    response = model.generate_content(prompt)
    return response.text # 정제하지 않은 문자열 그대로 반환