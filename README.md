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

## 📅 Timeline
- **Phase 1**: 기반 설계 및 환경 구축 (Setup)
  - 1-1. GitHub 저장소 및 프로젝트 보드 생성: README 초기화 및 Kanban 보드 세팅
  - 1-2. Notion 데이터베이스(DB) 설계: 필수 속성: 단어(Title), 요미가나(Text), 뜻(Text), 예문(Text), 상태(Select), 생성일(Date)
  - 1-3. API 권한 획득 및 보안 설정: Notion API(Internal Integration) 토큰 발급 및 DB 연결, Google Gemini API 키 발급 및 .env 환경변수 파일 설정
  - 1-4. Python 개발 환경 구축: 가상환경(venv) 설정 및 requirements.txt 작성
- **Phase 2**: 핵심 비즈니스 로직 개발 (Core Logic)
...
