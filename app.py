import streamlit as st
from translator import get_raw_response_from_gemini
from parser import parse_to_dict
import notion_writer as nw
import requests

if 'connected' not in st.session_state:
    st.session_state.connected = False
    st.session_state.token = ""
    st.session_state.db_id = ""
# page setting
st.set_page_config(page_title="일본어 단어 자동 등록기", page_icon="🇯🇵")

# SideBar: userSetting
with st.sidebar:
    st.title("Connection")

    # 세션 상태에 저장된 값이 있으면 기본값으로 불러옴
    input_token = st.text_input("Notion Token", type="password", value=st.session_state.get('token', ""))
    input_db_id = st.text_input("Database ID", value=st.session_state.get('db_id', ""))
    
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
                    st.success("연결 성공!")
                else:
                    st.error("연결 실패! 토큰이나 ID를 확인하세요!")
        else:
            st.warning("정보를 모두 입력해주세요")

# Main Screen
if st.session_state.connected:
    st.title("🇯🇵 일본어 단어 자동 등록 시스템")
    st.info(f"현재 연결된 Database ID: `{st.session_state.db_id[:8]}...`")
    st.write("모르는 단어 하나로 예문, 뉘앙스, JLPT 레벨까지 한번에 완벽 정리!")
    word_input = st.text_input("공부할 단어 입력: ", placeholder = "예: 기회")

    if st.button("AI 분석 및 노션 등록하기"):
        if not word_input:
            st.warning("단어를 입력해 주세요")
        else:    
            with st.spinner("AI 분석 중..."):
                # 1. Create AI Data
                st.write("Genimi AI가 단어 분석 중입니다...")
                raw_ai = get_raw_response_from_gemini(word_input)
                final_data = parse_to_dict(raw_ai)

                # 2. Check Duplicate
                st.write("노션 데이터베이스 중복 확인 중...")
                duplicate_url = nw.word_duplicate(final_data['word'], st.session_state.token, st.session_state.db_id)

                if duplicate_url:
                    st.warning(f"'{final_data['word']}'는 이미 등록된 단어")
                    st.link_button("기존 단어 보기", duplicate_url)
                else:
                    # Notion 등록
                    st.write("노션에 저장 중입니다...")
                    if nw.add_word(final_data, st.session_state.token, st.session_state.db_id):
                        st.success(f"'{final_data['word']}' 등록 성공!")
                        st.balloons() # Balloon effects

                        # 결과 요약
                        st.divider()
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("단어", final_data['word'], final_data['furigana'])
                        with col2:
                            st.metric("레벨", final_data['level'])
                        st.info(f"**뜻:**{final_data['meaning']}")
                    else:
                        st.error("노션 등록 실패.. 설정을 확인해 주세요")
else:
    st.title("시작하기")
    st.info("왼쪽 사이드바에서 노션 연결을 먼저 완료하세요!")