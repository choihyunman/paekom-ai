from fastapi import APIRouter
from pydantic import BaseModel
from app.utils.s3_utils import download_from_s3
from app.services.stt_service import run_stt

router = APIRouter()

class S3Request(BaseModel):
    s3_key: str

@router.post("/stt")
async def process_stt_from_s3(req: S3Request):
    """
    S3에서 오디오 다운로드 후 STT만 수행
    """
    try:
        local_path = f"/tmp/{req.s3_key.split('/')[-1]}"
        download_from_s3(req.s3_key, local_path)

        transcript = run_stt(local_path)

        return {
            "status": "success",
            "data": {
                "transcript": transcript
            }
        }

    except Exception as e:
        return {
            "status": "fail",
            "error": str(e)
        }