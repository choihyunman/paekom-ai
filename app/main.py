from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import stt_routes, report_routes

app = FastAPI(
    title="Paekom AI",
    description="비대면 상담 STT + 분석 API",
    version="0.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(stt_routes.router, prefix="/api", tags=["STT"])
app.include_router(report_routes.router, prefix="/api", tags=["Report"])

@app.get("/")
def root():
    return {"message": "Hello, Paekom-AI!"}