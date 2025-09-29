FROM python:3.11

WORKDIR /app

# 필수 패키지 설치 (ffmpeg 포함)
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# 파이썬 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 코드 복사
COPY ./app ./app

# 학습된 모델 폴더도 복사 (루트에 위치)
COPY ./my-korean-emotion-model ./my-korean-emotion-model

# 환경 변수로 모델 경로 지정
ENV EMOTION_MODEL_DIR=/app/my-korean-emotion-model

# FastAPI 실행 (Uvicorn)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]