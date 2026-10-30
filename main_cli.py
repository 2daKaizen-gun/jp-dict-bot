from translator import get_raw_response_from_gemini
from parser import parse_to_dict
from notion_writer import add_word, word_duplicate
from config import get_secret

def run_auto():
    # CLI는 .env의 Notion 자격 증명 사용
    token = get_secret("NOTION_TOKEN")
    database_id = get_secret("NOTION_DATABASE_ID")
    if not token or not database_id:
        print("NOTION_TOKEN / NOTION_DATABASE_ID를 .env에 설정하세요")
        return

    print("="*50)
    print("🇯🇵 일본어 단어 자동 등록 시스템 START")
    print("Gemini AI + Notion API Integration")
    print("="*50)
    print("종료: q or quit")

    while True:
        print("-"*50)
        search_word = input("공부할 단어 입력: ").strip()

        if search_word.lower() in ['q', 'quit']:
            print("System exit")
            break

        if not search_word:
            print("단어 입력하시오")
            continue

        try:
            print(f"\n '{search_word}' 데이터 생성 중..")
            # 1. Gemini API로 data 가져오기, 데이터 파싱, 정제 (phase 2)
            raw_ai = get_raw_response_from_gemini(search_word, "Auto-detect", database_id)
            final_data = parse_to_dict(raw_ai)

            if not final_data:
                print("AI 해석 실패, 다시 시도해 주세요")
                continue

            for data in final_data:
                # 2. 중복 확인
                target_word = data['word']
                existing_url = word_duplicate(target_word, token, database_id)

                if existing_url is None:
                    print(f"'{target_word}' 중복 확인 실패. 건너뜀")
                    continue

                if existing_url:
                    print(f"\n알림: '{target_word}'은(는) 이미 등록된 단어")
                    print(f"기존 페이지 확인: {existing_url}") # 링크
                    continue

                # 3. 중복 아닐 때 최종 저장
                print(f"{target_word} 등록 시작...")
                success, error = add_word(data, token, database_id)
                if success:
                    print("\n [Success] 등록 성공")
                    print(f"등록 단어: {data['word']} ({data.get('furigana', '')})")
                    print(f"의미: {data.get('meaning', '')}")
                    print("-" * 50)
                else:
                    print(f"오류가 발생했습니다: {error}")
        except Exception as e:
            print(f"오류 발생: {e}")

if __name__ == "__main__":
    try:
        run_auto()
    except KeyboardInterrupt:
        print("\n사용자가 강제 종료했습니다. 수고하셨습니다.")
    except Exception as e:
        # 그 외 예상 못한 에러 처리
        print(f"\n 시스템 오류 발생: {e}")
