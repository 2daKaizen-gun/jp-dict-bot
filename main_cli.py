from translator import get_raw_response_from_gemini
from parser import parse_to_dict
from notion_writer import add_word, word_duplicate
import time

def run_auto():
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
            final_data = parse_to_dict(get_raw_response_from_gemini(search_word))
            
            if not final_data:
                print("AI 해석 실패, 다시 시도해 주세요")
                continue
                
            # 2. 중복 확인
            target_word = final_data['word']
            existing_url = word_duplicate(target_word)

            if existing_url:
                print(f"\n알림: '{target_word}'은(는) 이미 등록된 단어")
                print(f"기존 페이지 확인: {existing_url}") # 링크
                continue
            
            # 3. 중복 아닐 때 최종 저장
            print(f"{target_word} 등록 시작...")
            if add_word(final_data):
                print("\n [Success] 등록 성공")
                print(f"등록 단어: {final_data['word']} ({final_data['furigana']})")
                print(f"의미: {final_data['meaning']}")
                print("-" * 50)
            else:
                print("오류가 발생했습니다")
        except ConnectionError:
            print("인터넷 연결 불안정. 네트워크 상태 확인")
        except KeyboardInterrupt:
            print("\n사용자에 의한 강제 종료")
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