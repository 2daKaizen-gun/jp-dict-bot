# jp-dict-bot(KR->JP Dictionary Automation)
> 일본어 학습 효율을 극대화하기 위한 개인 사전 자동화 프로젝트

## 📌 Project Overview
- **목적**: 학습 중 발견한 단어를 일일이 찾는 번거로움을 줄이고, AI를 통해 풍부한 예문과 함께 자동으로 저장합니다.
- **주요 기능**:
  - 어떤 언어든 입력 시 일본어 번역 및 예문 생성 (Gemini API)
  - Notion 데이터베이스 자동 기록 (Notion API)
  - 학습 상태 관리 및 복습 지원

## 🛠 Tech Stack
- **Language**: Python 3.14.0
- **Database**: Notion API
- **AI/LLM**: Google Gemini API
- **UI Framework**: Streamlit
- **Communication**: Requests
- **Deployment** : Streamlit Cloud
- **Security**: Streamlit Secrets

## ✅ Milestone
- **Phase 1**: Foundation & Environment Setup
  - [x] Phase 1-1: Initialize GitHub Repository & Project Board
  - [x] Phase 1-2: Design Notion Database Schema
  - [x] Phase 1-3: API Authorization & Security Setup(Notion, Gemini API & .env)
  - [x] Phase 1-4: Setup Python Development Environment(requirements.txt)

- **Phase 2**: Core Business Logic Development
  - [x] Phase 2-1: Translation & Data Extraction Module
  - [x] Phase 2-2: Gemini Prompt Engineering
  - [x] Phase 2-3: Data Parsing Module
  - [x] Phase 2-4: Local Integration Testing

- **Phase 3**: Notion Integration & Data Storage
  - [x] Phase 3-1: Develop Notion API Wrapper
  - [x] Phase 3-2: Data Mapping Logic
  - [x] Phase 3-3: Duplicate Prevention & Tracking Logic
  - [x] Phase 3-4: Exception Handling

- **Phase 4**: Productization & Web Interface Development
  - [x] Phase 4-1: Web UI Conversion (Streamlit/Web Framework)
  - [x] Phase 4-2: Dynamic Authentication & Session Management
  - [x] Phase 4-3: Batch Processing & Progress Visualization
  - [x] Phase 4-4: User Preference Persistence (Optional)
  - [ ] Phase 4-5: Multi-language Support

- **Phase 5**: Deployment, Documentation & Portfolio Finalization
  - [ ] Phase 5-1: Cloud Deployment
  - [ ] Phase 5-2: Comprehensive User Documentation (The "How-To")
  - [ ] Phase 5-3: Code Refactoring & Security Audit
  - [ ] Phase 5-4: Final Project Retrospective (The "Story")