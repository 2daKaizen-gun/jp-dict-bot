import json
import re

JSON_START = re.compile(r'\{|\[')

def parse_to_dict(raw_data):
    if not raw_data:
        return None

    clean_text = re.sub(r'```json|```', '', raw_data).strip()
    # 텍스트 안의 모든 JSON 객체/배열을 순서대로 추출
    results = []
    decoder = json.JSONDecoder()
    pos = 0

    while pos < len(clean_text):
        # 현재 위치 이후에서 다음 '{' 또는 '[' 탐색
        match = JSON_START.search(clean_text, pos)
        if not match:
            break

        pos = match.start()
        try:
            # 위치로부터 유효한 JSON 읽어옴
            obj, end = decoder.raw_decode(clean_text, pos)

            # 리스트면 합치고, 객체면 추가
            if isinstance(obj, list):
                results.extend(obj)
            else:
                results.append(obj)
            pos = end # 읽은 만큼 위치 이동
        except json.JSONDecodeError:
            pos += 1 # 에러 나면 한 칸 이동해 다시 찾음

    # 단어 데이터(dict)만 남김
    results = [r for r in results if isinstance(r, dict) and r.get('word')]
    return results if results else None
