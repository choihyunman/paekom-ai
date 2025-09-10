import boto3
from app.config import settings

s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    region_name=settings.aws_region,
)

def download_from_s3(key: str, local_path: str) -> str:
    """S3에서 음성 파일 다운로드"""
    s3_client.download_file(settings.aws_s3_bucket, key, local_path)
    return local_path