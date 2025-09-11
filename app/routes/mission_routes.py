from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.mission_service import generate_feedback

router = APIRouter()

# 요청 Body 스키마
class MissionRequest(BaseModel):
    title: str
    content: str
    category: str
    memo: str | None = None


@router.post("/mission")
async def mission_feedback(req: MissionRequest):
    """
    미션 피드백 생성 API
    """
    try:
        feedback = generate_feedback(req)
        return {
            "status": "success",
            "data": {
                "feedback": feedback
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))