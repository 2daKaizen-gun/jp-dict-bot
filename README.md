# jp-dict-bot(KR->JP Dictionary Automation)
> 일본어 학습 효율을 극대화하기 위한 개인 사전 자동화 프로젝트

## 📌 Project Overview
- **목적**: 학습 중 발견한 단어를 일일이 찾는 번거로움을 줄이고, AI를 통해 풍부한 예문과 함께 자동으로 저장합니다.
- **주요 기능**:
  - 한국어 단어 입력 시 일본어 번역 및 예문 생성 (Gemini API)
  - Notion 데이터베이스 자동 기록 (Notion API)
  - 학습 상태 관리 및 복습 지원

## 🛠 Tech Stack
- **Language**: Python 3.14.0
- **Database**: Notion
- **AI/LLM**: Google Gemini API
- **Libraries**: `notion-client`, `python-dotenv`

## ✅ Milestone
- **Phase 1**: 기반 설계 및 환경 구축 (Setup)
  - [x] Phase 1-1: GitHub 저장소 및 프로젝트 보드 생성: README 초기화, Kanban 보드 세팅