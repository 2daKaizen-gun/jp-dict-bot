from translator import get_raw_response_from_gemini
from parser import parse_to_dict
from notion_writer import add_word
import time

def run_auto():
    print("="*50)
    print("🇯🇵 일본어 단어 자동 등록 시스템 START")
    print("="*50)

    search_word = input("공부할 단어 입력: ").strip()

    if not search_word:
        print("단어 입력하시오")
        return
    
    try:
        print(f"\n '{search_word}'에 대한 데이터 생성 중..")
        # Gemini API로 data 가져오기 (phase 2-1, 2-2)
        raw_response = get_raw_response_from_gemini(search_word)

        print("데이터를 정제하고 있습니다...")
        # 데이터 파싱, 정제 (phase 2-3)
        final_data = parse_to_dict(raw_response)

        if not final_data:
            print("오류 발생")
            return
        
        # 4. 노션에 최종 저장 (Phase 3-1, 3-2)
        print("노션 데이터베이스에 등록 시도...")
        notion_result = add_word(final_data)

        # Result
        if notion_result:
            print("\n [Success] 등록 성공")
            print(f"등록 단어: {final_data['word']} ({final_data['furigana']})")
            print(f"의미: {final_data['meaning']}")
            print("-" * 50)
        else:
            print("오류가 발생했습니다")
    except Exception as e:
        print(f"오류 발생: {e}")
if __name__ == "__main__":
    run_auto()