import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_secret(key, default=None):
    """환경 변수 우선, 없으면 Streamlit Secrets에서 조회 (secrets 파일이 없어도 안전)"""
    value = os.getenv(key)
    if value:
        return value
    try:
        return st.secrets.get(key, default)
    except Exception:
        # 로컬에 secrets.toml이 없으면 st.secrets 접근 시 예외 발생
        return default

def is_personal_db(database_id):
    """개인용(한국어 스키마) DB인지 판별"""
    my_id = get_secret("NOTION_DATABASE_ID")
    return bool(my_id) and database_id == my_id
