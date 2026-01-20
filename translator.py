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
    
    # 2. 구조적 추출을 위한 프롬프트 구성
    prompt = f"""
    Please translate the Korean word '{word}' into Japanese and provide learning data.
    You MUST respond ONLY in JSON format with the following keys:
    - word: Japanese Kanji or Hiragana
    - furigana: Reading in Hiragana
    - meaning: Korean meaning
    - level: Estimated JLPT level (N1~N5)
    - example: A natural Japanese sentence using the word
    - interpretation: Korean translation of the example
    
    Respond in raw JSON format without any markdown tags or code blocks.
    """

    try:
        response = model.generate_content(prompt)
        
        # 3. 결과 파싱 (JSON 변환)
        # AI 결과물에 혹시라도 섞여 있을 코드 블록 기호(```json)를 제거합니다.
        raw_json = response.text.strip().replace('```json', '').replace('```', '')
        data = json.loads(raw_json)
        
        return data

    except Exception as e:
        print(f"데이터 추출 중 오류 발생: {e}")
        return None

# 테스트 실행
if __name__ == "__main__":
    test_word = "결심"
    result = fetch_vocabulary_data(test_word)
    if result:
        print(json.dumps(result, indent=4, ensure_ascii=False))