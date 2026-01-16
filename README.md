# GMS Chatbot with News

Streamlit 기반 챗봇 애플리케이션으로 GMS(GPT 5 - nano)를 활용하여 대화하고 Google News RSS 피드를 통해 최신 뉴스를 제공합니다.

## 📋 기능

- **AI 챗봇**: GMS (GPT 5 - nano) API를 통한 대화
- **뉴스 통합**: Google News RSS 기반 최신 뉴스 수집
- **안전한 API Key 관리**: 환경 변수를 통한 보안
- **실시간 상호작용**: Streamlit 기반의 반응형 UI

## 🚀 설치 및 실행

### 1. 필수 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 GMS API Key를 설정하세요:

```bash
# .env 파일 생성 및 수정
cp .env.example .env

# .env 파일에 실제 API Key 입력
# GMS_API_KEY=your_actual_gms_api_key_here
# GMS_MODEL=gpt-5-nano
# GMS_API_ENDPOINT=https://api.example.com/v1
```

### 3. 애플리케이션 실행

```bash
streamlit run main.py
```

브라우저에서 `http://localhost:8501`로 접속합니다.

## 📁 프로젝트 구조

```
chatbot/
├── main.py                 # Streamlit 메인 애플리케이션
├── config.py              # 애플리케이션 설정 (환경 변수 로드)
├── chat_handler.py        # GMS API 통신 담당
├── news_handler.py        # Google News RSS 수집 담당
├── requirements.txt       # 의존 패키지
├── .env                   # 환경 변수 (실제 값)
├── .env.example           # 환경 변수 템플릿
└── README.md              # 이 파일
```

## 🔧 주요 구성 요소

### config.py
- 환경 변수 로드 및 관리
- `python-dotenv`를 통한 보안

### chat_handler.py
- GMS API와 통신
- 메시지 전송 및 응답 처리
- 뉴스 요약 기능

### news_handler.py
- Google News RSS 피드 파싱
- 카테고리별 뉴스 수집 (최신, 비즈니스, 기술, 과학)

### main.py
- Streamlit UI 구성
- 사이드바 설정 (카테고리, 파라미터 조절)
- 채팅 인터페이스
- 뉴스 표시

## ⚙️ 설정

### 창의성 (Temperature)
- 범위: 0.0 ~ 2.0
- 낮을수록: 일관되고 정확한 응답
- 높을수록: 창의적이고 다양한 응답

### 최대 토큰 수 (Max Tokens)
- 범위: 100 ~ 2000
- 응답의 최대 길이 제어

## 🔐 보안

- ❌ API Key가 코드에 절대 포함되지 않음
- ✅ `.env` 파일을 통한 환경 변수 관리
- ✅ `.gitignore`에 `.env` 파일 추가 권장

```
# .gitignore
.env
__pycache__/
*.pyc
```

## 🐛 트러블슈팅

### API Key 오류
```
ValueError: GMS_API_KEY 환경 변수가 설정되지 않았습니다.
```
→ `.env` 파일에서 `GMS_API_KEY`가 올바르게 설정되었는지 확인하세요.

### 뉴스 로드 실패
→ 인터넷 연결 확인 및 RSS 피드 URL 확인

## 📝 라이선스

This project is open source and available under the MIT License.

## 🤝 기여

이 프로젝트에 대한 개선 사항이나 버그 리포트는 언제든 환영합니다!
