import streamlit as st

# page setting (다른 Streamlit 호출보다 먼저 실행)
st.set_page_config(page_title="JP Dictionary Bot | Auto Sync", page_icon="🇯🇵")

from translator import get_raw_response_from_gemini
from parser import parse_to_dict
import notion_writer as nw
from config import get_local_env

# Initialization: 자격 증명은 세션에만 보관
# (서버 파일에 저장하면 배포 환경에서 모든 방문자가 같은 토큰을 공유하게 됨)
if 'connected' not in st.session_state:
    st.session_state.connected = False
    # 로컬 .env 파일이 있을 때만 기본값으로 사용
    # (Streamlit Cloud는 Secrets를 환경 변수로도 노출하므로 os.getenv 사용 금지)
    st.session_state.token = get_local_env("NOTION_TOKEN")
    st.session_state.db_id = get_local_env("NOTION_DATABASE_ID")

def show_guide():
    with st.expander("Pre: Connection Guide", expanded=True):
        st.markdown(f"""
        - This system requires a specific Notion database structure to function correctly
        - Please follow these steps to set up your environment:

        ### 1. Duplicate the Official Template (Required)
        - Visit ['JP Dictionary' Template]({ "https://noble-pail-b93.notion.site/2f497a6e755980238ef1df44b80868fb?v=2f497a6e7559816e8081000ccd5f8bd3" })
        - Click **'Duplicate'** at the top right to copy it to your workspace
        - **Note:** Do not rename column headers (e.g., Word, Meaning) as it may break the sync

        ### 2. Create a Notion Integration
        - Visit [Notion My-Integrations](https://www.notion.so/my-integrations)
        - Click **'+ New Integration'**, name it, and submit
        - Copy your **'Internal Integration Token'**
        
        ### 3. Grant Database Access
        - Open your **duplicated database** in Notion
        - Click the three dots (**`...`**) at the top right -> **'Connect to'** (or Add Connections)
        - Search for your Integration name and confirm

        ### 4. Locate Database ID
        - Check your database URL
        - The **32-character string** between the workspace name and the `?v=` is your ID
        - Example: `...notion.site/` **[THIS_32_CHAR_STRING]** `?v=...`
        """)

        st.info("Pro Tip: Credentials are kept only for this session. When running locally, set `NOTION_TOKEN` and `NOTION_DATABASE_ID` in `.env` to pre-fill them")

# SideBar: userSetting
with st.sidebar:
    st.title("Connection")

    # 세션 상태에 저장된 값이 있으면 기본값으로 불러옴
    input_token = st.text_input("Notion Token", type="password", value=st.session_state.get('token', ""))
    input_db_id = st.text_input("Database ID", value=st.session_state.get('db_id', ""))

    # 연결 test Button
    if st.button("Connect to Notion"):
        if input_token and input_db_id:
            # 데이터베이스 조회로 검사
            with st.spinner("Establishing connection..."):
                if nw.check_connection(input_token, input_db_id):
                    st.session_state.token = input_token
                    st.session_state.db_id = input_db_id
                    st.session_state.connected = True
                    st.success("Successfully Connected!")
                else:
                    st.error("Connection Failed. Please verify your Token and ID!")
        else:
            st.warning("Please fill in all connection fields")

# Main Screen
if st.session_state.connected:
    st.title("🇯🇵 Japanese Vocabulary Auto-Sync")
    st.info(f"Connected to Database ID: `{st.session_state.db_id[:8]}...`")
    # JLPT 목표 설정
    st.subheader("Learning Preferences")
    target_level = st.selectbox(
        "Target JLPT Level:",
        ["Auto-detect", "N1", "N2", "N3", "N4", "N5"],
        help = "AI will optimize examples and nuances based on the selected level"
    )
    st.divider()
    st.write("Enter a word to automatically generate JLPT levels, contextual examples, and usage nuances!")
    word_input = st.text_input("Input Words (Supports Korean, English, etc. Separated by commas(',')): ", placeholder = "e.g. 기회, Opportunity")

    if st.button("Analyze & Sync to Notion"):
        if not word_input:
            st.warning("Please enter words")
        else:
            # 단어 리스트 화
            word_list = [w.strip() for w in word_input.split(",") if w.strip()]
            total = len(word_list)
            st.info(f"Processing {total} word(s)...")
            
            # progress bar
            progress_bar = st.progress(0)
            failed = 0

            for i, word in enumerate(word_list):
                # 개별 단어 처리 상태를 보여주는 status 창
                with st.status(f"Processing '{word}'... ({i+1}/{total})") as status:
                    # 1. Create AI Data
                    st.write("Generative AI is analyzing...")
                    
                    raw_ai = get_raw_response_from_gemini(word, target_level, st.session_state.db_id)
                    final_data = parse_to_dict(raw_ai)

                    if not final_data:
                        st.error(f"Failed to analyze '{word}'. Invalid AI response format")
                        status.update(label=f"Failed: '{word}'", state="error")
                        failed += 1
                        progress_bar.progress((i + 1) / total)
                        continue # 이 단어는 건너뛰고 다음 단어로 진행

                    # 2. Check Duplicate
                    word_failed = False
                    for data in final_data:
                        st.write("Checking for duplicates in Notion...")
                        duplicate_url = nw.word_duplicate(data['word'], st.session_state.token, st.session_state.db_id)

                        if duplicate_url is None:
                            st.error(f"Could not check duplicates for '{data['word']}'. Skipped")
                            word_failed = True
                        elif duplicate_url:
                            st.warning(f"'{data['word']}' already exists in your database")
                            st.link_button("View Existing Entry", duplicate_url)
                        else:
                            # Notion 등록
                            st.write("Syncing to Notion...")
                            success, error = nw.add_word(data, st.session_state.token, st.session_state.db_id)
                            if success:
                                st.success(f"'{data['word']}' successfully synced!")
                                # 결과 요약 표시
                                st.write(f"**Meaning:** {data.get('meaning', '-')} | **Level:** {data.get('level', '-')}")
                            else:
                                st.error(f"Failed to sync '{data['word']}': {error}")
                                word_failed = True

                    if word_failed:
                        failed += 1
                        status.update(label=f"Finished '{word}' with errors", state="error")
                    else:
                        status.update(label=f"Done with '{word}'!", state="complete")

                # 3. Progress bar update
                progress_bar.progress((i + 1) / total)

            if failed:
                st.warning(f"Batch processing complete with {failed} failed word(s)")
            else:
                st.balloons() # balloon effect
                st.success("Batch processing complete!")
else:
    st.title("Get Started")
    show_guide()
    st.info("Please complete the Notion connection in the sidebar to begin!")