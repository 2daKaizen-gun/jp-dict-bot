import os
import requests
from notion_client import Client
from dotenv import load_dotenv

# .env에서 파일 로드
load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# notion client reset
notion = Client(auth=NOTION_TOKEN)

def add_word(data):
    """
    파싱된 data받아 notion database에 새 페이지 생성
    """
    try:
        new_page = notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "단어": {
                    "title": [
                        {"text": {"content": data['word']}}
                    ]
                },
                "요미가나": {
                    "rich_text": [
                        {"text": {"content": data['furigana']}}
                    ]
                },
                "뜻": {
                    "rich_text": [
                        {"text": {"content": data['meaning']}}
                    ]
                },
                "상태": {
                    "select": {"name": "미학습"}
                },
                "레벨": {
                    "multi_select": [
                        {"name": data['level']} 
                    ]
                },
                "예문": {
                    "rich_text": [
                        {"text": {"content": data['example_ja']}}
                    ]
                },
                "해석": {
                    "rich_text": [
                        {"text": {"content": data['example_ko']}}
                    ]
                },
                "뉘앙스": {
                    "rich_text": [
                        {"text": {"content": data['nuance']}}
                    ]
                }
            }
        )
        return new_page
    except Exception as e:
        print(f"노션 저장 중 오류 발생: {e}")
        return None

def word_duplicate(word):
    """
    라이브러리를 거치지 않고 직접 HTTP 통신으로 중복 확인
    중복 확인 후, 이미 존재하면 해당 페이지의 URL을 반환하고 아니면 None을 반환합니다.
    """
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28", # 노션 API
        "Content-Type": "application/json"
    }
    payload = {
        "filter": {
            "property": "단어",
            "title": {"equals": word}
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            results = response.json().get("results", [])
            if results:
                # 중복된 첫 번째 페이지의 URL을 가져옴
                return results[0].get("url") 
            return None
        return None
    except Exception as e:
        print(f"중복 확인 중 오류: {e}")
        return None