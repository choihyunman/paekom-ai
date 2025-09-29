import torch
import logging
import kss
import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# 로그 설정
logger = logging.getLogger("uvicorn")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)

class AnalyzeService:
    """
    상담 텍스트 분석 서비스
    - 문장 단위 감정 분류 (학습된 KcELECTRA 파인튜닝 모델)
    - 세션 전체 감정 요약
    """

    labels = ["부정", "중립", "긍정"]
    label_map = {"긍정": "POSITIVE", "중립": "NEUTRAL", "부정": "NEGATIVE"}

    def __init__(self, model_path: str | None = None):
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # 기본값: 프로젝트 루트에 있는 my-korean-emotion-model 폴더
        default_path = os.path.join(base_dir, "../../my-korean-emotion-model")
        model_path = model_path or os.getenv("EMOTION_MODEL_DIR", default_path)

        logger.info(f"[AnalyzeService] 모델 경로: {model_path}")

        # ✅ 코랩에서 학습한 모델 불러오기
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_path,
            local_files_only=True
        )
        self.model.eval()

        # 모델 내부의 id2label, label2id 확인 로그
        logger.info(f"[AnalyzeService] id2label: {self.model.config.id2label}")
        logger.info(f"[AnalyzeService] label2id: {self.model.config.label2id}")

    def classify_emotion(self, text: str) -> str:
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = torch.nn.functional.softmax(logits, dim=-1)[0].tolist()
            pred = int(torch.argmax(torch.tensor(probs)).item())

            # 로그 출력
            logger.info(f"[분석 대상] {text}")
            for i, p in enumerate(probs):
                logger.info(f"  - {self.labels[i]}: {p:.4f}")
            logger.info(f"[예측 감정] {self.labels[pred]}")

        return self.labels[pred]

    def analyze(self, transcript: str) -> dict:
        sentences = [s.strip() for s in kss.split_sentences(transcript) if s.strip()]
        if not sentences:
            return {"emotion": "NEUTRAL", "evidence": {"POSITIVE": 0, "NEUTRAL": 100, "NEGATIVE": 0}}

        emotions = [self.classify_emotion(s) for s in sentences]

        total = len(emotions)
        counts = {label: emotions.count(label) for label in self.labels}
        ratios = {
            "POSITIVE": round((counts["긍정"] / total) * 100),
            "NEUTRAL": round((counts["중립"] / total) * 100),
            "NEGATIVE": round((counts["부정"] / total) * 100)
        }

        session_emotion_kor = max(counts, key=counts.get)
        session_emotion_eng = self.label_map[session_emotion_kor]

        return {"emotion": session_emotion_eng, "evidence": ratios}