import requests
from config import is_personal_db

NOTION_API_URL = "https://api.notion.com/v1"
REQUEST_TIMEOUT = 10 # seconds
MAX_TEXT_LENGTH = 2000 # Notion rich_text 최대 길이
ALLOWED_LEVELS = ["N1", "N2", "N3", "N4", "N5"]

def get_notion_headers(token: str) -> dict:
    """Notion API 통신 위한 공통 header 반환"""
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28", # 노션 API
        "Content-Type": "application/json"
    }

def get_dbSchema(database_id):
    if is_personal_db(database_id):
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

def _text(value):
    """AI 응답 값을 Notion 텍스트 형식으로 변환 (누락/None 안전 처리)"""
    content = str(value).strip() if value is not None else ""
    return [{"text": {"content": content[:MAX_TEXT_LENGTH]}}]

def _error_message(response):
    try:
        return response.json().get("message", response.text)
    except ValueError:
        return response.text


def check_connection(token, database_id):
    """Token & DB ID로 데이터베이스 접근 가능한지 확인"""
    url = f"{NOTION_API_URL}/databases/{database_id}"
    try:
        response = requests.get(url, headers=get_notion_headers(token), timeout=REQUEST_TIMEOUT)
        return response.status_code == 200
    except requests.RequestException:
        return False


def word_duplicate(word, token, database_id):
    """사용자가 입력한 token & ID 사용해 중복 확인"""
    url = f"{NOTION_API_URL}/databases/{database_id}/query"
    headers = get_notion_headers(token)
    schema = get_dbSchema(database_id)

    payload = {
        "filter": {
            "property": schema["word"], # 동적 컬럼명 사용
            "title": {"equals": word}
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            results = response.json().get("results", [])
            return results[0].get("url") if results else False # 중복 없으면 False
        print(f"Duplicate check failed ({response.status_code}): {_error_message(response)}")
        return None
    except requests.RequestException as e:
        print(f"Duplicate check error: {e}")
        return None


def add_word(data, token, database_id):
    """사용자 지정 노션 데이터베이스에 단어 등록
    Returns: (성공 여부, 에러 메시지)"""

    # 스키마 및 레벨 데이터 정규화
    schema = get_dbSchema(database_id)

    # Level Data Normalization
    # AI 응답 없으면 기본값 = 'N3', 대문자 변환
    raw_level = str(data.get('level') or 'N3').upper().strip()

    # 허용된 태그 목록이 아니면 'N3'로 고정 (데이터 무결성 확보)
    final_level = raw_level if raw_level in ALLOWED_LEVELS else "N3"

    # API 설정
    url = f"{NOTION_API_URL}/pages"
    headers = get_notion_headers(token)

    # 페이로드 구성(동적 키 매핑)
    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            schema["word"]: {"title": _text(data.get('word'))},
            schema["furigana"]: {"rich_text": _text(data.get('furigana'))},
            schema["meaning"]: {"rich_text": _text(data.get('meaning'))},
            schema["status"]: {"select": {"name": schema["status_val"]}},
            schema["level"]: {"multi_select": [{"name": final_level}]},
            schema["example"]: {"rich_text": _text(data.get('example_ja'))},
            schema["translation"]: {"rich_text": _text(data.get('example'))},
            schema["nuance"]: {"rich_text": _text(data.get('nuance'))}
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            return True, None
        return False, f"Notion Sync Error: {_error_message(response)}"
    except requests.RequestException as e:
        return False, f"Notion API Exception: {e}"
