import streamlit as st
from translator import get_raw_response_from_gemini
from parser import parse_to_dict
import notion_writer as nw
import json
import os

CONFIG_FILE = "user_config.json"

def save_config(token, db_id):
    """사용자 설정을 JSON 파일로 저장"""
    with open(CONFIG_FILE, "w") as f:
        json.dump({"token": token, "db_id": db_id}, f)

def load_config():
    """저장된 설정 불러오기"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return None

# 초기화 전 저장된 설정 불러오기
saved_data = load_config()

if 'connected' not in st.session_state:
    st.session_state.connected = False
    # 저장된 데이터 있으면 세션에 미리 넣기
    st.session_state.token = saved_data['token'] if saved_data else ""
    st.session_state.db_id = saved_data['db_id'] if saved_data else ""

# page setting
st.set_page_config(page_title="일본어 단어 자동 등록기", page_icon="🇯🇵")

def show_guide():
    with st.expander("시작 전: 노션 연동 가이드", expanded=False):
        st.markdown("""
        이 시스템을 이용하려면 Notion과의 연동이 필요합니다.
        아래 순서대로 설정을 완료해 주세요.

        ### 1. Notion integration 생성
        - [노션 내 integration](https://www.notion.so/my-integrations) 페이지에 접속
        - **'+ New integration'** 버튼 클릭해 이름 입력, 생성
        - 생성된 **'프라이빗 API 통합 토큰'**을 복사
        
        ### 2. 데이터베이스 연결 추가
        - 사용할 노션 데이터베이스 페이지로 이동
        - 우측 상단 점 세 개(**`...`**)를 클릭 -> 맨 아래 **'연결 추가'** 선택
        - 방금 만든 integration 이름을 검색해서 추가

        ### 3. Database ID 확인
        - 데이터베이스 주소(URL) 확인
        - `https://www.notion.so/myworkspace/` 와 `?v=` 사이에 있는 **32자리 문자열**이 ID
        """)

        st.info("팁: 한 번 연결에 성공 시 사이드바의 '정보 기억하기'를 체크")

# SideBar: userSetting
with st.sidebar:
    st.title("Connection")

    # 세션 상태에 저장된 값이 있으면 기본값으로 불러옴
    input_token = st.text_input("Notion Token", type="password", value=st.session_state.get('token', ""))
    input_db_id = st.text_input("Database ID", value=st.session_state.get('db_id', ""))
    
    # 정보 기억 checkbox
    remember = st.checkbox("이 브라우저에서 정보 기억하기", value=bool(saved_data))
    
    # 연결 test Button
    if st.button("Connect to Notion"):
        if input_token and input_db_id:
            # 간단한 query로 검사
            with st.spinner("연결 확인 중..."):
                is_valid = nw.word_duplicate("연결테스트", input_token, input_db_id)
                # 중복 확인 함수가 응답이 오면 연결 성공으로 간주함
                if is_valid is not None or is_valid == False:
                    st.session_state.token = input_token
                    st.session_state.db_id = input_db_id
                    st.session_state.connected = True
                    
                    # checkbox 선택 시 파일로 save
                    if remember:
                        save_config(input_token, input_db_id)
                    elif os.path.exists(CONFIG_FILE):
                        os.remove(CONFIG_FILE) # 체크 해제 시 파일 삭제
                    
                    st.success("연결 성공!")
                else:
                    st.error("연결 실패! 토큰이나 ID를 확인하세요!")
        else:
            st.warning("정보를 모두 입력해주세요")

# Main Screen
if st.session_state.connected:
    st.title("🇯🇵 일본어 단어 자동 등록 시스템")
    st.info(f"현재 연결된 Database ID: `{st.session_state.db_id[:8]}...`")
    # JLPT 목표 설정
    st.subheader("학습 설정")
    target_level = st.selectbox(
        "목표 JLPT LEVEL:",
        ["자동 판정", "N1", "N2", "N3", "N4", "N5"],
        help = "선택한 레벨로 AI가 예문, 설명을 최적화"
    )
    st.divider()
    st.write("모르는 단어 하나로 JLPT 레벨, 설정 레벨에 따른 예문, 뉘앙스까지 한번에 완벽 정리!")
    word_input = st.text_input("공부할 단어(한글, english, etc.) 입력(','로 구분): ", placeholder = "예: 기회, Opportunity")

    if st.button("AI 분석 및 노션 등록하기"):
        if not word_input:
            st.warning("단어를 입력해 주세요")
        else:
            # 단어 리스트 화
            word_list = [w.strip() for w in word_input.split(",") if w.strip()]
            total = len(word_list)
            st.info(f"총 {total}개의 단어 처리 시작...")
            
            # progress bar
            progress_bar = st.progress(0)

            for i, word in enumerate(word_list):
                # 개별 단어 처리 상태를 보여주는 status 창
                with st.status(f"'{word}' 처리 중... ({i+1}/{total})") as status:
                    # 1. Create AI Data
                    st.write("Genimi AI가 단어 분석 중입니다...")
                    
                    raw_ai = get_raw_response_from_gemini(word, target_level)
                    final_data = parse_to_dict(raw_ai)

                    if not final_data:
                        st.error(f"'{word}' 분석 실패.. AI 응답 형식이 올바르지 않습니다.")
                        continue # 이 단어는 건너뛰고 다음 단어로 진행
                    
                    # 2. Check Duplicate
                    for data in final_data:
                        st.write("노션 데이터베이스 중복 확인 중...")
                        duplicate_url = nw.word_duplicate(data['word'], st.session_state.token, st.session_state.db_id)

                        if duplicate_url:
                            st.warning(f"'{data['word']}'는 이미 등록된 단어")
                            st.link_button("기존 단어 보기", duplicate_url)
                        else:
                            # Notion 등록
                            st.write("노션에 저장 중입니다...")
                            if nw.add_word(data, st.session_state.token, st.session_state.db_id):
                                st.success(f"'{data['word']}' 등록 성공!")
                                # 결과 요약 표시
                                st.write(f"뜻: {data['meaning']} | 레벨: {data['level']}")
                            else:
                                st.error(f"등록 실패: {data['word']}")
                    status.update(label=f"'{word}' 완료!", state="complete")
                
                # 3. Progress bar update
                progress_bar.progress((i + 1) / total)
            
            st.balloons() # balloon effect
            st.success("모든 작업 완료되었습니다!")
else:
    st.title("시작하기")
    show_guide()
    st.info("왼쪽 사이드바에서 노션 연결을 먼저 완료하세요!")