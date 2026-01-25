import json
import re

def parse_to_dict(raw_data):
        clean_text = re.sub(r'```json|```', '', raw_data).strip()
        # 가장 바깥쪽의 { } 괄호 안쪽 내용만 추출
        results = []
        decoder = json.JSONDecoder()
        pos = 0
        
        while pos < len(clean_text):  
            match = re.search(r'\{|\[', clean_text, re.DOTALL)
            if not match:
                break
            
            pos += match.start()
            try:
                # 위치로부터 유효한 JSON 읽어옴
                obj, index = decoder.raw_decode(clean_text[pos:])

                # 리스트면 합치고, 객체면 추가
                if isinstance(obj, list):
                    results.extend(obj)
                else:
                    results.append(obj)
                pos += index # 읽은 만큼 위치 이동
            except json.JSONDecodeError:
                pos += 1 # 에러 나면 한 칸 이동해 다시 찾음
        return results if results else None