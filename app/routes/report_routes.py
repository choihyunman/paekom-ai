from fastapi import APIRouter
from pydantic import BaseModel
from app.services.analyze_service import AnalyzeService
from app.services.solar_service import SolarService

# 라우터 선언
router = APIRouter()

# 요청 스키마
class ReportRequest(BaseModel):
    transcript: str

# 서비스 초기화
analyzer = AnalyzeService()
solar = SolarService()

@router.post("/report")
async def generate_report(req: ReportRequest):
    """
    상담 STT 텍스트를 받아서
    - Solar API로 요약 + 주요 이슈
    - AnalyzeService로 감정/근거 분석
    결과를 합쳐 리포트 반환
    """
    try:
        transcript = req.transcript

        # 1. Solar 요약 + 주요 이슈
        solar_json = solar.summarize(transcript)

        # 2. 감정/근거 분석
        analysis_result = analyzer.analyze(transcript)

        # 성공 응답
        return {
            "status": "success",
            "data": {
                "summary": solar_json.get("summary", ""),
                "main_issues": solar_json.get("main_issues", []),
                "emotion": analysis_result["emotion"],
                "evidence": analysis_result["evidence"],
                "overall_assessment": "자동 분석 완료"
            }
        }

    except Exception as e:
        # 실패 응답도 같은 구조
        return {
            "status": "fail",
            "error": str(e)
        }