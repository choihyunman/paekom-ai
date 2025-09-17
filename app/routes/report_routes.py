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
    try:
        transcript = req.transcript

        solar_json = solar.summarize(transcript)
        analysis_result = analyzer.analyze(transcript)

        return {
            "status": "success",
            "data": {
                "summary": solar_json.get("summary", ""),
                "issues": solar_json.get("issues", []),
                "emotion": analysis_result["emotion"],
                "evidence": analysis_result["evidence"],
                "overall_assessment": solar_json.get("overall_assessment", "분석 결과를 받아올 수 없습니다.")
            }
        }

    except Exception as e:
        return {
            "status": "fail",
            "error": str(e)
        }