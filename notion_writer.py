import os
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
# test code
if __name__ == "__main__":
    # serve data
    test_data = {
        "word": "決心",
        "furigana": "けっしん",
        "meaning": "결심",
        "level": "N3",
        "example_ja": "日本での就職を決心しました。",
        "example_ko": "일본에서의 취업을 결심했습니다.",
        "nuance": "강한 의지를 가질 때 사용합니다."
    }
    result = add_word(test_data)
    if result:
        print("노션 등록 성공")