import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class AnalyzeService:
    """
    상담 텍스트 분석 서비스
    - 문장 단위 감정 분류 (KcELECTRA)
    - 세션 전체 감정 요약
    - issues는 제거 (Solar가 제공하므로 중복 방지)
    """

    labels = ["부정", "중립", "긍정"]

    def __init__(self):
        model_name = "beomi/KcELECTRA-base"  # 한국어 대화체에 강한 모델
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)

    def classify_emotion(self, text: str) -> str:
        """
        문장 단위 감정 분류
        """
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            pred = torch.argmax(probs, dim=1).item()
        return self.labels[pred]

    def analyze(self, transcript: str) -> dict:
        """
        상담 텍스트 전체 분석
        """
        # 1. 문장 단위 분리
        sentences = [s.strip() for s in transcript.replace("?", ".").replace("!", ".").split(".") if s.strip()]

        if not sentences:
            return {"emotion": "중립", "evidence": "데이터 없음"}

        # 2. 감정 분류 (문장 단위)
        emotions = [self.classify_emotion(s) for s in sentences]

        # 3. 감정 비율 계산
        total = len(emotions)
        counts = {label: emotions.count(label) for label in self.labels}
        ratios = {label: round((counts[label] / total) * 100, 1) for label in self.labels}

        # 4. 세션 전체 감정 = 최빈값
        session_emotion = max(counts, key=counts.get)

        # 5. 결과 반환 (issues 제거)
        return {
            "emotion": session_emotion,
            "evidence": f"부정:{ratios['부정']}%, 중립:{ratios['중립']}%, 긍정:{ratios['긍정']}%"
        }
