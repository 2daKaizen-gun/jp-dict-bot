from translator import get_raw_response_from_gemini
from parser import parse_to_dict

word = input("공부할 단어 입력: ")

# 1. AI에게 답변 받기
raw_text = get_raw_response_from_gemini(word)

# 2. 답변 정제
final_data = parse_to_dict(raw_text)

# 3. Result
print(f"단어: {final_data['word']}")
print(f"뉘앙스: {final_data['nuance']}")