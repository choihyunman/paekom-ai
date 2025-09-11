from __future__ import annotations
from app.services.solar_service import SolarService

solar = SolarService()

def generate_feedback(mission: MissionRequest) -> str:
    """
    미션 피드백 생성
    MissionRequest는 routes/mission_routes.py 안에 정의돼 있음
    __future__ import 덕분에 import 안 해도 타입 참조 가능
    """
    mission_text = (
        f"제목: {mission.title}\n"
        f"내용: {mission.content}\n"
        f"카테고리: {mission.category}\n"
        f"메모: {mission.memo or ''}"
    )
    return solar.feedback(mission_text)