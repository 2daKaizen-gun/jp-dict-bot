import streamlit as st
from translator import get_raw_response_from_gemini
from parser import parse_to_dict
import notion_writer as nw
import json
import os

# Constants
CONFIG_FILE = "user_config.json"

def save_config(token, db_id):
    """Saves user configuration to a local JSON file"""
    with open(CONFIG_FILE, "w") as f:
        json.dump({"token": token, "db_id": db_id}, f)

def load_config():
    """Loads saved configuration from the local JSON file"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return None

# Initialization: Load saved credentials
saved_data = load_config()

if 'connected' not in st.session_state:
    st.session_state.connected = False
    # 저장된 데이터 있으면 세션에 미리 넣기
    st.session_state.token = saved_data['token'] if saved_data else ""
    st.session_state.db_id = saved_data['db_id'] if saved_data else ""

# page setting
st.set_page_config(page_title="JP Dictionary Bot | Auto Sync", page_icon="🇯🇵")

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

        st.info("Pro Tip: Check **'Remember Me'** in the sidebar to save your credentials locally")

# SideBar: userSetting
with st.sidebar:
    st.title("Connection")

    # 세션 상태에 저장된 값이 있으면 기본값으로 불러옴
    input_token = st.text_input("Notion Token", type="password", value=st.session_state.get('token', ""))
    input_db_id = st.text_input("Database ID", value=st.session_state.get('db_id', ""))
    
    # 정보 기억 checkbox
    remember = st.checkbox("Remember me on this browser", value=bool(saved_data))
    
    # 연결 test Button
    if st.button("Connect to Notion"):
        if input_token and input_db_id:
            # 간단한 query로 검사
            with st.spinner("Establishing connection..."):
                is_valid = nw.word_duplicate("ConnectionCheck", input_token, input_db_id)
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
    word_input = st.text_input("Input Words (Supports Korean, English, etc. Separated by commas(',')): ", placeholder = "예: 기회, Opportunity")

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

            for i, word in enumerate(word_list):
                # 개별 단어 처리 상태를 보여주는 status 창
                with st.status(f"Processing '{word}'... ({i+1}/{total})") as status:
                    # 1. Create AI Data
                    st.write("Generative AI is analyzing...")
                    
                    raw_ai = get_raw_response_from_gemini(word, target_level, st.session_state.db_id)
                    final_data = parse_to_dict(raw_ai)

                    if not final_data:
                        st.error(f"Failed to analyze '{word}'. Invalid AI response format")
                        continue # 이 단어는 건너뛰고 다음 단어로 진행
                    
                    # 2. Check Duplicate
                    for data in final_data:
                        st.write("Checking for duplicates in Notion...")
                        duplicate_url = nw.word_duplicate(data['word'], st.session_state.token, st.session_state.db_id)

                        if duplicate_url:
                            st.warning(f"'{data['word']}' already exists in your database")
                            st.link_button("View Existing Entry", duplicate_url)
                        else:
                            # Notion 등록
                            st.write("Syncing to Notion...")
                            if nw.add_word(data, st.session_state.token, st.session_state.db_id):
                                st.success(f"'{data['word']}' successfully synced!")
                                # 결과 요약 표시
                                st.write(f"**Meaning:** {data['meaning']} | **Level:** {data['level']}")
                            else:
                                st.error(f"Failed to sync: {data['word']}")
                    status.update(label=f"Done with '{word}'!", state="complete")
                
                # 3. Progress bar update
                progress_bar.progress((i + 1) / total)
            
            st.balloons() # balloon effect
            st.success("Batch processing complete!")
else:
    st.title("Get Started")
    show_guide()
    st.info("Please complete the Notion connection in the sidebar to begin!")