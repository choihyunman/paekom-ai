import os
import json
from openai import OpenAI, OpenAIError

class SolarService:
    """
    업스테이지 Solar API 호출 서비스 (요약)
    """

    def __init__(self):
        api_key = os.getenv("SOLAR_API_KEY")
        if not api_key:
            raise RuntimeError("SOLAR_API_KEY 환경 변수가 설정되지 않았습니다.")

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.upstage.ai/v1"
        )

    def summarize(self, text: str) -> dict:
        try:
            response = self.client.chat.completions.create(
                model="solar-pro2",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "너는 상담 내용을 분석해서 구조화된 리포트를 생성하는 요약기야.\n"
                            "출력은 반드시 JSON 형식으로만 반환해. 다른 말은 절대 하지 마.\n\n"
                            "형식 예시:\n"
                            "{\n"
                            '  \"summary\": \"...\",\n'
                            '  \"main_issues\": [\"...\", \"...\"]\n'
                            "}"
                        )
                    },
                    {"role": "user", "content": text}
                ],
                temperature=0.3,
                max_tokens=500
            )

            content = response.choices[0].message.content

            # 문자열인 경우 → 코드블록 제거
            if isinstance(content, str):
                cleaned = content.strip()
                if cleaned.startswith("```"):
                    # ```json ... ``` 제거
                    cleaned = cleaned.strip("`")
                    cleaned = cleaned.replace("json\n", "").replace("json", "").strip()
                return json.loads(cleaned)

            # dict로 내려온 경우 → 그대로 반환
            return content

        except OpenAIError as e:
            raise RuntimeError(f"Solar API 호출 실패: {str(e)}")
        except json.JSONDecodeError:
            raise RuntimeError(f"Solar 응답 JSON 파싱 실패. 원본 응답: {content}")
        except Exception as e:
            raise RuntimeError(f"요약 처리 중 알 수 없는 오류 발생: {str(e)}")
