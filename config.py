import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

class Config:
    """애플리케이션 설정"""
    
    # GMS (GPT 5 - nano) 설정
    GMS_API_KEY = os.getenv("GMS_API_KEY")
    GMS_MODEL = os.getenv("GMS_MODEL", "gpt-5-nano")
    GMS_API_ENDPOINT = os.getenv("GMS_API_ENDPOINT", "https://api.example.com/v1")
    
    # 검증
    if not GMS_API_KEY:
        raise ValueError("GMS_API_KEY 환경 변수가 설정되지 않았습니다. .env 파일을 확인하세요.")
    
    # Streamlit 설정
    STREAMLIT_THEME = "light"
    PAGE_TITLE = "GMS Chatbot with News"
    PAGE_ICON = "🤖"
    
    # 뉴스 설정
    NEWS_FETCH_INTERVAL = 3600  # 1시간
    MAX_NEWS_ITEMS = 10
    # 기본 최대 토큰 수
    DEFAULT_MAX_TOKENS = 8000
