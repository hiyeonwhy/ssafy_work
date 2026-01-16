import streamlit as st
from datetime import datetime, timedelta
from config import Config
from chat_handler import ChatHandler
from news_handler import NewsHandler

class ChatbotApp:
    """GMS Chatbot with News 애플리케이션"""
    
    def __init__(self):
        self.config = Config
        self.setup_page()
        self.initialize_session_state()
    
    def setup_page(self):
        """Streamlit 페이지 설정"""
        st.set_page_config(
            page_title=self.config.PAGE_TITLE,
            page_icon=self.config.PAGE_ICON,
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # 스타일 설정
        st.markdown("""
            <style>
            .main {
                padding: 2rem;
            }
            .chat-message {
                padding: 1rem;
                border-radius: 0.5rem;
                margin: 0.5rem 0;
            }
            .user-message {
                background-color: #e3f2fd;
                border-left: 4px solid #2196f3;
            }
            .assistant-message {
                background-color: #f5f5f5;
                border-left: 4px solid #888;
            }
            </style>
        """, unsafe_allow_html=True)
    
    def initialize_session_state(self):
        """세션 상태 초기화"""
        if "messages" not in st.session_state:
            st.session_state.messages = []
            # 초기 안내 메시지: 사이트 실행 시 사용자에게 도움 안내
            st.session_state.messages.append({"role": "assistant", "content": "챗봇이 무엇을 도와드릴까요?"})
        if "news_cache" not in st.session_state:
            # news_cache 구조: { category: { 'items': [...], 'fetched_at': datetime } }
            st.session_state.news_cache = {}
    
    def render_header(self):
        """헤더 렌더링"""
        st.title("🤖 GMS Chatbot with News")
        st.markdown("---")
    
    def render_sidebar(self):
        """사이드바 렌더링"""
        with st.sidebar:
            st.header("⚙️ 설정")
            
            # 뉴스 카테고리
            st.subheader("📰 뉴스")
            categories = NewsHandler.get_available_categories()
            selected_category = st.selectbox("뉴스 카테고리:", categories, key="news_category")
            
            # 뉴스 검색어
            st.subheader("🔎 뉴스 검색")
            news_query = st.text_input("검색어 (예: 삼성전자)", value="", key="news_query")

            # developer 역할 프롬프트 (optional)
            st.subheader("🛠️ Developer Prompt")
            developer_instruction = st.text_input("개발자 역할 지시문 (role=developer)", value="Answer in Korean", key="developer_instruction")
            
            # 뉴스 새로고침
            if st.button("🔄 뉴스 새로고침"):
                st.session_state.news_cache = {}
                st.rerun()
            
            # 채팅 파라미터
            st.subheader("🎯 채팅 설정")
            temperature = st.slider("창의성 (Temperature):", 0.0, 2.0, 0.7, 0.1)
            
            # 대화 초기화
            if st.button("🗑️ 대화 초기화"):
                st.session_state.messages = []
                st.rerun()
            
            st.markdown("---")
            st.markdown("**정보**")
            st.info(f"모델: {self.config.GMS_MODEL}\nAPI: {self.config.GMS_API_ENDPOINT}")
            
            return selected_category, temperature, developer_instruction, news_query
    
    def render_news_sidebar(self, selected_category: str, news_query: str = ""):
        """뉴스 표시 (오른쪽 사이드바)"""
        st.subheader("📰 최신 뉴스")
        
        try:
            # 검색어가 있으면 검색 결과 사용
            if news_query and news_query.strip():
                news_items = NewsHandler.search_news(news_query.strip(), category=selected_category, max_items=self.config.MAX_NEWS_ITEMS)
            else:
                # 캐시된 뉴스 또는 새로 가져오기 (타임스탬프 기반)
                cache_entry = st.session_state.news_cache.get(selected_category)
                need_fetch = True
                if cache_entry:
                    fetched_at = cache_entry.get("fetched_at")
                    if isinstance(fetched_at, datetime):
                        age = (datetime.now() - fetched_at).total_seconds()
                        if age < self.config.NEWS_FETCH_INTERVAL:
                            need_fetch = False
                if need_fetch:
                    news_items = NewsHandler.fetch_news(
                        selected_category,
                        max_items=self.config.MAX_NEWS_ITEMS
                    )
                    st.session_state.news_cache[selected_category] = {"items": news_items, "fetched_at": datetime.now()}
                else:
                    news_items = cache_entry.get("items", [])
            
            # 뉴스 표시
            if news_items:
                for news in news_items[:5]:
                    with st.expander(news["title"][:50] + "..."):
                        st.markdown(f"**출처:** {news['source']}")
                        st.markdown(f"**작성일:** {news['published']}")
                        st.markdown(news["summary"][:200] + "...")
                        st.markdown(f"[전체 기사 읽기]({news['link']})")
            else:
                st.warning("뉴스를 가져올 수 없습니다.")
        except Exception as e:
            st.error(f"뉴스 로드 실패: {str(e)}")
    
    def render_chat_history(self):
        """채팅 히스토리 렌더링"""
        st.subheader("💬 대화")
        
        chat_container = st.container(height=400)
        
        with chat_container:
            for message in st.session_state.messages:
                role = message.get("role", "user")
                content = message.get("content", "")
                if role == "user":
                    emoji = "🙋"
                    css_class = "user-message"
                    label = "당신"
                elif role == "assistant":
                    emoji = "🤖"
                    css_class = "assistant-message"
                    label = "Assistant"
                elif role == "developer":
                    emoji = "🛠️"
                    css_class = "assistant-message"
                    label = "Developer"
                else:
                    emoji = "⚙️"
                    css_class = "assistant-message"
                    label = role

                st.markdown(f"""
                    <div class="chat-message {css_class}">
                    <strong>{emoji} {label}:</strong> {content}
                    </div>
                """, unsafe_allow_html=True)
    
    def handle_user_input(self, temperature: float):
        """사용자 입력 처리"""
        user_input = st.chat_input("메시지를 입력하세요...", key="main_chat_input")

        if user_input:
            # 즉시 사용자 메시지 표시
            st.session_state.messages.append({"role": "user", "content": user_input})
            # 기사 검색/요청 판단: 간단 휴리스틱
            def detect_article_search(text: str):
                t = text.lower()
                keywords = ["기사", "뉴스", "요약", "summary", "article", "search", "검색", "요청"]
                matched = any(k in t for k in keywords)
                if not matched:
                    return False, None

                # 키워드 추출: 불용어 제거
                remove_tokens = ["기사", "뉴스", "요약", "요약해줘", "요약해", "검색", "검색해줘", "관련", "최신", "오늘", "정리해줘", "정리해"]
                s = t
                for tok in remove_tokens:
                    s = s.replace(tok, " ")
                # 영어 stopwords
                for tok in ["summary", "article", "news", "search"]:
                    s = s.replace(tok, " ")
                # strip punctuation
                import re
                s = re.sub(r"[^\w\s\u3131-\u318E\uAC00-\uD7A3]", " ", s)
                s = " ".join([w for w in s.split() if len(w) > 1])
                keyword = s.strip()
                if not keyword:
                    # fallback: use the original text as keyword
                    keyword = text.strip()
                return True, keyword

            is_search, search_keyword = detect_article_search(user_input)
            if is_search:
                try:
                    # 선택된 카테고리 사용
                    category = st.session_state.get("news_category", "최신뉴스")
                    news_items = NewsHandler.search_news(search_keyword, category=category, max_items=self.config.MAX_NEWS_ITEMS)
                    summary = NewsHandler.summarize_news(news_items, max_articles=self.config.MAX_NEWS_ITEMS)
                    st.session_state.messages.append({"role": "assistant", "content": summary})
                except Exception as e:
                    st.error(f"기사 검색 중 오류 발생: {e}")
                return

            # 동기적으로 API 호출을 수행하여 응답이 바로 표시되도록 함
            try:
                with st.spinner("응답을 생성 중입니다..."):
                    chat_handler = ChatHandler()
                    system_message = "당신은 도움이 되는 어시스턴트입니다."
                    messages = []
                    developer_text = st.session_state.get("developer_instruction", "")
                    if developer_text:
                        messages.append({"role": "developer", "content": developer_text})
                    messages.append({"role": "system", "content": system_message})
                    messages = messages + st.session_state.messages

                    max_tokens = getattr(self.config, "DEFAULT_MAX_TOKENS", 8000)
                    response = chat_handler.send_message(
                        messages,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )

                # 어시스턴트 응답 추가
                st.session_state.messages.append({"role": "assistant", "content": response})

            except Exception as e:
                st.error(f"오류 발생: {str(e)}")
    
    def render_footer(self):
        """푸터 렌더링"""
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #888; font-size: 0.85rem;">
            <p>GMS Chatbot with News | Powered by Streamlit</p>
            <p>API Key는 환경 변수로 안전하게 관리됩니다.</p>
        </div>
        """, unsafe_allow_html=True)

    
    
    def run(self):
        """애플리케이션 실행"""
        self.render_header()
        # 자동 새로고침: 뉴스 업데이트 주기에 맞춰 페이지를 자동으로 리로드
        try:
            interval_sec = int(self.config.NEWS_FETCH_INTERVAL)
        except Exception:
            interval_sec = 0
        if interval_sec and interval_sec > 0:
            # 클라이언트에서 페이지를 자동 새로고침
            st.components.v1.html(f"<script>setTimeout(()=>location.reload(), {interval_sec * 1000});</script>", height=0)
        
        # 사이드바
        selected_category, temperature, developer_instruction, news_query = self.render_sidebar()
        
        # 메인 콘텐츠
        col1, col2 = st.columns([2, 1])

        # 사용자 입력을 먼저 처리 so pending flag gets set before processing
        self.handle_user_input(temperature)

        with col1:
            self.render_chat_history()
            # API 호출은 handle_user_input에서 동기적으로 처리함

        with col2:
            self.render_news_sidebar(selected_category, news_query=news_query)
        
        st.markdown("---")
        
        # 푸터
        self.render_footer()


def main():
    """메인 진입점"""
    app = ChatbotApp()
    app.run()


if __name__ == "__main__":
    main()
