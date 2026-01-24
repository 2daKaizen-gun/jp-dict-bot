import requests

def word_duplicate(word, token, database_id):
    """사용자가 입력한 token & ID 사용해 중복 확인"""
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    headers = {
        "Authorization": f"Bearer {token}",
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
        print(f"[Debug] Status Code: {response.status_code}")
        if response.status_code != 200:
            print(f"[Debug] Error Detail: {response.json()}")
        if response.status_code == 200:
            results = response.json().get("results", [])
            return results[0].get("url") if results else False # 중복 없으면 False
        return None
    except Exception as e:
        print(f"중복 확인 중 오류: {e}")
        return None
    

def add_word(data, token, database_id):
    """사용자 지정 노션 데이터베이스에 단어 등록"""
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "단어": {"title": [{"text": {"content": data['word']}}]},
            "요미가나": {"rich_text": [{"text": {"content": data['furigana']}}]},
            "뜻": {"rich_text": [{"text": {"content": data['meaning']}}]},
            "상태": {"select": {"name": "미학습"}},
            "레벨": {"multi_select": [{"name": data['level']}]},
            "예문": {"rich_text": [{"text": {"content": data['example_ja']}}]},
            "해석": {"rich_text": [{"text": {"content": data['example_ko']}}]},
            "뉘앙스": {"rich_text": [{"text": {"content": data['nuance']}}]}
        }
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.status_code == 200