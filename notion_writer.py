import requests
import os
import streamlit as st

def get_notion_headers(token: str) -> dict:
    """Notion API 통신 위한 공통 header 반환"""
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28", # 노션 API
        "Content-Type": "application/json"
    }

def get_dbSchema(database_id):
    my_id = os.getenv("NOTION_DATABASE_ID") or st.secrets.get("NOTION_DATABASE_ID")
    if database_id == my_id:
        return {
            "word": "단어", "furigana": "요미가나", "meaning": "뜻",
            "status": "상태", "level": "레벨", "example": "예문",
            "translation": "해석", "nuance": "뉘앙스", "status_val": "미학습"
        }
    else:
        return {
            "word": "Word", "furigana": "Furigana", "meaning": "Meaning",
            "status": "Status", "level": "Level", "example": "Example",
            "translation": "Translation", "nuance": "Nuance", "status_val": "Not Started"
        }


def word_duplicate(word, token, database_id):
    """사용자가 입력한 token & ID 사용해 중복 확인"""
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    headers = get_notion_headers(token)
    schema = get_dbSchema(database_id)
    
    payload = {
        "filter": {
            "property": schema["word"], # 동적 컬럼명 사용
            "title": {"equals": word}
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"[Debug] Status Code: {response.status_code}")
        if response.status_code != 200:
            print(f"[Debug] Error Detail: {response.json()}")
        if response.status_code == 200:
            results = response.json().get("results", [])
            return results[0].get("url") if results else False # 중복 없으면 False
        return None
    except Exception as e:
        print(f"Duplicate check error: {e}")
        return None
    

def add_word(data, token, database_id):
    """사용자 지정 노션 데이터베이스에 단어 등록"""
    
    # 스키마 및 레벨 데이터 정규화
    schema = get_dbSchema(database_id)

    # Level Data Normalization
    # AI 응답 없으면 기본값 = 'N3', 대문자 변환
    raw_level = data.get('level', 'N3').upper().strip()
    
    # 허용된 태그 목록이 아니면 'N3'로 고정 (데이터 무결성 확보)
    allowed_levels = ["N1", "N2", "N3", "N4", "N5"]
    final_level = raw_level if raw_level in allowed_levels else "N3"
    
    # API 설정
    url = "https://api.notion.com/v1/pages"
    headers = get_notion_headers(token)

    # 페이로드 구성(동적 키 매핑)
    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            schema["word"]: {"title": [{"text": {"content": data['word']}}]},
            schema["furigana"]: {"rich_text": [{"text": {"content": data['furigana']}}]},
            schema["meaning"]: {"rich_text": [{"text": {"content": data['meaning']}}]},
            schema["status"]: {"select": {"name": schema["status_val"]}},
            schema["level"]: {"multi_select": [{"name": final_level}]},
            schema["example"]: {"rich_text": [{"text": {"content": data['example_ja']}}]},
            schema["translation"]: {"rich_text": [{"text": {"content": data['example']}}]},
            schema["nuance"]: {"rich_text": [{"text": {"content": data['nuance']}}]}
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            st.error(f"Notion Sync Error: {response.json().get('message')}")
        return response.status_code == 200
    except Exception as e:
        st.error(f"Notion API Exception: {e}")
        return False