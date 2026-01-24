import streamlit as st
from translator import get_raw_response_from_gemini
from parser import parse_to_dict
import notion_writer as nw

# page setting
st.set_page_config(page_title="일본어 단어 자동 등록기", page_icon="🇯🇵")

# SideBar: userSetting
with st.sidebar:
    st.title("노션 연결 설정")
    st.info("노션 API 정보 입력")
    user_token = st.text_input("Notion API Token", type="password")
    user_db_id = st.text_input("Database ID")
    st.markdown("---")
    st.caption("입력 정보는 서버에 저장되지 않고 현재 세션에서만 사용됨")

# Main Screen
st.title("🇯🇵 일본어 단어 자동 등록 시스템")
st.write("모르는 단어 하나로 예문, 뉘앙스, JLPT 레벨까지 한번에 완벽 정리!")

word_input = st.text_input("공부할 단어 입력: ", placeholder = "예: 기회")

if st.button("AI 분석 및 노션 등록"):
    if not user_token or not user_db_id:
        st.warning("먼저 사이드바에 노션 설정을 완료해 주세요!")
    elif not word_input:
        st.error("단어를 입력해 주세요!")
    else:
        with st.status("작업 진행 중...", expanded=True) as status:
            # 1. Create AI Data
            st.write("Genimi AI가 단어 분석 중입니다...")
            raw_ai = get_raw_response_from_gemini(word_input)
            final_data = parse_to_dict(raw_ai)

            # 2. Check Duplicate
            st.write("노션 데이터베이스 중복 확인 중...")
            duplicate_url = nw.word_duplicate(final_data['word'], user_token, user_db_id)

            if duplicate_url:
                st.warning(f"'{final_data['word']}'는 이미 등록된 단어")
                st.link_button("기존 단어 보기", duplicate_url)
                status.update(label="중복 확인 완료", state="complete")
            else:
                # Notion 등록
                st.write("노션에 저장 중입니다...")
                if nw.add_word(final_data, user_token, user_db_id):
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
                    status.update(label="등록 완료!", state="complete")
                else:
                    st.error("노션 등록 실패.. 설정을 확인해 주세요")
                    status.update(label="오류 발생", state="error")