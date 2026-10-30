import os
import streamlit as st
from dotenv import load_dotenv, dotenv_values

ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")

load_dotenv(ENV_FILE)

def get_local_env(key, default=""):
    """로컬 .env 파일에서만 조회 (환경 변수/Streamlit Secrets는 무시)
    배포 환경에는 .env가 없으므로 항상 default 반환"""
    if not os.path.exists(ENV_FILE):
        return default
    return dotenv_values(ENV_FILE).get(key) or default

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
