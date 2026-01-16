import requests
from typing import List, Dict
from config import Config

class ChatHandler:
    """GMS (GPT-5-nano) API를 통한 채팅 처리"""

    def __init__(self):
        self.api_key = Config.GMS_API_KEY
        self.model = Config.GMS_MODEL
        self.api_endpoint = Config.GMS_API_ENDPOINT.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def send_message(
        self,
        messages: List[Dict],
        temperature: float = 0.7,   # UI용 (API에는 안 보냄)
        max_tokens: int = 500
    ) -> str:
        """GMS API에 메시지 전송 및 응답 받기"""

        if not self.api_key:
            raise ValueError("GMS_API_KEY가 설정되어 있지 않습니다.")

        if not isinstance(messages, list) or not messages:
            raise ValueError("messages는 비어있지 않은 리스트여야 합니다.")

        for m in messages:
            if not isinstance(m, dict) or "role" not in m or "content" not in m:
                raise ValueError("각 메시지는 'role'과 'content' 키를 가진 dict여야 합니다.")

        payload = {
            "model": self.model,
            "messages": messages,
            "max_completion_tokens": max_tokens
        }

        try:
            url = f"{self.api_endpoint}/chat/completions"
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code != 200:
                try:
                    err = response.json()
                except Exception:
                    err = response.text
                raise Exception(f"API 오류 ({response.status_code}): {err}")

            result = response.json()

            # =========================
            # ✅ 응답 파싱: 여러 포맷을 안전하게 처리
            # 우선순위: OpenAI-style 'choices' -> gpt-5-nano 'output_text'/'output' -> 기타
            # =========================

            # 0️⃣ OpenAI / GMS(프록시) 스타일: choices[].message.content 또는 choices[].text
            if isinstance(result, dict) and "choices" in result:
                choices = result.get("choices") or []
                if isinstance(choices, list) and len(choices) > 0:
                    choice = choices[0]
                    if isinstance(choice, dict):
                        # message.content 형태
                        msg = choice.get("message")
                        if isinstance(msg, dict):
                            content = msg.get("content") or msg.get("text")
                            if isinstance(content, str) and content.strip():
                                return content.strip()

                        # 직접 text 필드
                        text = choice.get("text")
                        if isinstance(text, str) and text.strip():
                            return text.strip()

            # 1️⃣ gpt-5-nano 특유의 output_text 필드
            if "output_text" in result and result["output_text"]:
                return result["output_text"].strip()

            # 2️⃣ output 배열 구조 (content items)
            output_text = ""
            for item in result.get("output", []):
                for content in item.get("content", []):
                    if content.get("type") == "output_text":
                        output_text += content.get("text", "")

            if output_text.strip():
                return output_text.strip()

            # 3️⃣ fallback: 응답에서 첫 번째 문자열값을 찾아 반환
            def find_first_str(obj):
                if isinstance(obj, str):
                    return obj
                if isinstance(obj, dict):
                    for v in obj.values():
                        res = find_first_str(v)
                        if res:
                            return res
                if isinstance(obj, list):
                    for item in obj:
                        res = find_first_str(item)
                        if res:
                            return res
                return None

            found = find_first_str(result)
            if found:
                return found.strip()

            # 4️⃣ 그래도 없으면 빈 문자열 반환
            return ""

        except requests.exceptions.RequestException as e:
            raise Exception(f"API 요청 실패: {e}")
        except Exception as e:
            raise Exception(f"채팅 처리 중 오류 발생: {e}")

    def create_news_summary(self, news_items: List[Dict]) -> str:
        """뉴스 요약 프롬프트 생성"""
        if not news_items:
            return "현재 사용 가능한 뉴스가 없습니다."

        parts = ["최신 뉴스:"]
        for i, n in enumerate(news_items[:5], 1):
            parts.append(f"{i}. {n.get('title')}")
        return "\n".join(parts)
