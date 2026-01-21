from translator import get_raw_response_from_gemini
from parser import parse_to_dict
import time

def run_test():
    print("="*50)
    print("test start")
    print("="*50)

    search_word = input("공부할 단어 입력: ").strip()

    if not search_word:
        print("단어 입력하시오")
        return
    
    try:
        print(f"\n '{search_word}'에 대한 데이터 요청 중..")
        start_time = time.time()

        # Gemini API로 data 가져오기 (phase 2-1, 2-2)
        raw_response = get_raw_response_from_gemini(search_word)

        # 데이터 파싱, 정제 (phase 2-3)
        final_data = parse_to_dict(raw_response)

        end_time = time.time()

        # Result
        if final_data:
            print(f"\n소요시간: {end_time - start_time:.2f}초")
            print("-" * 30)
            print(f"단어: {final_data.get('word')}")
            print(f"읽기: {final_data.get('furigana')}")
            print(f"의미: {final_data.get('meaning')}")
            print(f"레벨: {final_data.get('level')}")
            print(f"예문: {final_data.get('example_ja')}")
            print(f"해석: {final_data.get('example_ko')}")
            print(f"뉘앙스: {final_data.get('nuance')}")
            print("-" * 30)
            print("노션에 등록될 준비 완료")
        else:
            print("오류가 발생했습니다")
    except Exception as e:
        print(f"오류 발생: {e}")
if __name__ == "__main__":
    run_test()