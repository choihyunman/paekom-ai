import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class AnalyzeService:
    """
    상담 텍스트 분석 서비스
    - 문장 단위 감정 분류 (KcELECTRA)
    - 세션 전체 감정 요약
    """

    labels = ["부정", "중립", "긍정"]  # 감정 판단 순서 (Korean)
    label_map = {
        "긍정": "POSITIVE",
        "중립": "NEUTRAL",
        "부정": "NEGATIVE"
    }

    def __init__(self):
        model_name = "beomi/KcELECTRA-base"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)

    def classify_emotion(self, text: str) -> str:
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            pred = torch.argmax(probs, dim=1).item()
        return self.labels[pred]

    def analyze(self, transcript: str) -> dict:
        sentences = [s.strip() for s in transcript.replace("?", ".").replace("!", ".").split(".") if s.strip()]

        if not sentences:
            return {
                "emotion": "NEUTRAL",
                "evidence": {
                    "POSITIVE": 0,
                    "NEUTRAL": 100,
                    "NEGATIVE": 0
                }
            }

        emotions = [self.classify_emotion(s) for s in sentences]

        total = len(emotions)
        counts = {label: emotions.count(label) for label in self.labels}
        # evidence 순서를 "POSITIVE", "NEUTRAL", "NEGATIVE"로 맞추기 위해 아래와 같이 처리
        ratios = {
            "POSITIVE": round((counts["긍정"] / total) * 100),
            "NEUTRAL": round((counts["중립"] / total) * 100),
            "NEGATIVE": round((counts["부정"] / total) * 100)
        }

        # 세션 전체 감정 = 최빈값
        session_emotion_kor = max(counts, key=counts.get)
        session_emotion_eng = self.label_map[session_emotion_kor]

        return {
            "emotion": session_emotion_eng,
            "evidence": ratios
        }
