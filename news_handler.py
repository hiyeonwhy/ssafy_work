import feedparser
from typing import List, Dict

class NewsHandler:
    """Google News RSS 기반 뉴스 수집"""

    NEWS_FEEDS = {
        "최신뉴스": "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko",
        "비즈니스": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFZxY0d4U0FtVnVHZ0pDVXlnQVAB?oc=5",
        "기술": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp0Y0d4U0FtVnVHZ0pDVXlnQVAB?oc=5",
        "과학": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFZxY0d4U0FtVnVHZ0pDVXlnQVAB?oc=5"
    }

    @staticmethod
    def fetch_news(category: str = "최신뉴스", max_items: int = 10) -> List[Dict]:
        try:
            feed_url = NewsHandler.NEWS_FEEDS.get(category, NewsHandler.NEWS_FEEDS["최신뉴스"])
            feed = feedparser.parse(feed_url)
            news_list: List[Dict] = []
            for entry in feed.entries[:max_items]:
                news_list.append({
                    "title": entry.get("title", "제목 없음"),
                    "link": entry.get("link", ""),
                    "summary": entry.get("summary", ""),
                    "published": entry.get("published", ""),
                    "source": entry.get("source", {}).get("title", "Google News") if entry.get("source") else "Google News"
                })
            return news_list
        except Exception as e:
            print(f"뉴스 수집 중 오류: {e}")
            return []

    @staticmethod
    def get_available_categories() -> List[str]:
        return list(NewsHandler.NEWS_FEEDS.keys())

    @staticmethod
    def search_news(keyword: str, category: str = "최신뉴스", max_items: int = 50) -> List[Dict]:
        """피드에서 키워드로 뉴스 검색 (제목, 요약 대상)

        Args:
            keyword: 검색어 (대소문자 무시)
            category: 피드 카테고리
            max_items: 반환할 최대 항목 수

        Returns:
            키워드에 매칭되는 뉴스 딕셔너리 리스트
        """
        if not keyword:
            return []

        import urllib.parse
        try:
            # 우선 Google News의 검색 RSS를 사용하여 쿼리별로 정확한 결과를 수집
            query = urllib.parse.quote(keyword)
            search_url = f"https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"
            feed = feedparser.parse(search_url)
            news_list: List[Dict] = []
            for entry in feed.entries[:max_items]:
                news_list.append({
                    "title": entry.get("title", "제목 없음"),
                    "link": entry.get("link", ""),
                    "summary": entry.get("summary", ""),
                    "published": entry.get("published", ""),
                    "source": entry.get("source", {}).get("title", "Google News") if entry.get("source") else "Google News"
                })
            # 결과가 충분하지 않으면 카테고리 피드에서 추가 필터링 수행
            if not news_list:
                items = NewsHandler.fetch_news(category, max_items=max_items * 2)
                kw = keyword.lower()
                filtered = []
                for it in items:
                    title = (it.get("title") or "").lower()
                    summary = (it.get("summary") or "").lower()
                    if kw in title or kw in summary:
                        filtered.append(it)
                    if len(filtered) >= max_items:
                        break
                return filtered

            return news_list
        except Exception as e:
            print(f"뉴스 검색 중 오류: {e}")
            return []

    @staticmethod
    def summarize_news(news_items: List[Dict], max_articles: int = 5) -> str:
        """뉴스 항목 리스트를 사람이 읽기 쉬운 요약 텍스트로 변환하여 반환한다.

        - 기사 제목, 출처, 작성일, 간단요약, 링크를 포함
        - 단순 링크 나열이 아닌 요약·정리 형태로 반환
        """
        if not news_items:
            return "검색된 기사가 없습니다."

        items = news_items[:max_articles]
        parts = [f"기사 요약 (총 {len(news_items)}건 중 상위 {len(items)}건):\n"]
        for i, it in enumerate(items, 1):
            title = it.get("title", "제목 없음")
            source = it.get("source", "")
            published = it.get("published", "")
            summary = it.get("summary", "").strip()
            # 짧은 요약 한두 문장으로 줄이기
            short = summary.split('.')
            short_text = short[0].strip() + '.' if short and short[0].strip() else (summary[:200] + '...')

            parts.append(f"{i}. {title}\n출처: {source} | 작성일: {published}\n요약: {short_text}\n링크: {it.get('link', '')}\n")

        # 간단한 종합 코멘트 (문장 조합)
        headlines = ' / '.join([it.get('title', '') for it in items if it.get('title')])
        parts.append(f"종합: 주요 기사 제목 — {headlines}")
        return "\n".join(parts)

        
