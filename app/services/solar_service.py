import os
import json
from openai import OpenAI, OpenAIError

class SolarService:
    """
    업스테이지 Solar API 호출 서비스 (요약 + 평가)
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
                            "너는 30년 경력의 상담가처럼 따뜻하고 전문적으로 상담 내용을 요약하고 진단해주는 전문가야.\n"
                            "사용자가 보낸 상담 내용을 기반으로 아래의 형식대로 리포트를 JSON으로 출력해줘.\n"
                            "반드시 다른 말 없이 JSON만 반환해야 해.\n\n"
                            "형식 예시:\n"
                            "{\n"
                            '  "summary": "상담 내용을 객관적으로 정리한 요약",\n'
                            '  "main_issues": ["문제1", "문제2", ...],\n'
                            '  "overall_assessment": "현실을 따뜻하게 진단하고 응원과 조언을 주는 평가 문장"\n'
                            "}\n\n"
                            "overall_assessment는 현재 상황을 진단하면서도 공감, 응원, 조언의 톤을 가져야 하며,\n"
                            "지나친 비판 없이 상담자에게 힘이 될 수 있는 문장을 작성해야 해."
                        )
                    },
                    {"role": "user", "content": text}
                ],
                temperature=0.3,
                max_tokens=600
            )

            content = response.choices[0].message.content

            # 문자열로 응답 시 코드블록 제거
            if isinstance(content, str):
                cleaned = content.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.strip("`")
                    cleaned = cleaned.replace("json\n", "").replace("json", "").strip()
                return json.loads(cleaned)

            # dict로 내려온 경우
            return content

        except OpenAIError as e:
            raise RuntimeError(f"Solar API 호출 실패: {str(e)}")
        except json.JSONDecodeError:
            raise RuntimeError(f"Solar 응답 JSON 파싱 실패. 원본 응답: {content}")
        except Exception as e:
            raise RuntimeError(f"요약 처리 중 알 수 없는 오류 발생: {str(e)}")
        
    
    def feedback(self, mission_text: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model="solar-pro2",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "너는 따뜻하고 친근한 30년차 상담가야.\n"
                            "사용자가 보낸 '미션 기록'을 보고 간단한 격려와 피드백을 해줘.\n"
                            "분석이나 진단 말고, 진심 어린 응원과 칭찬, 조언 톤이면 돼.\n"
                            "⚠️ 출력은 반드시 따옴표 없이 순수 텍스트로만 반환해야 해."
                        )
                    },
                    {"role": "user", "content": mission_text}
                ],
                temperature=0.7,
                max_tokens=150
            )

            content = response.choices[0].message.content.strip()

            # 혹시라도 따옴표로 감싸져 있으면 제거
            if content.startswith('"') and content.endswith('"'):
                content = content[1:-1]

            return content

        except Exception as e:
            raise RuntimeError(f"Solar Feedback 호출 실패: {str(e)}")