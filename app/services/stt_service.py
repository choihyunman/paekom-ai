import whisper

# Whisper 모델 로드 (CPU면 small/tiny 권장)
model = whisper.load_model("small")

def run_stt(audio_file_path: str) -> str:
    """
    오디오 파일을 텍스트로 변환
    """
    try:
        result = model.transcribe(audio_file_path, language="ko")
        return result["text"]
    except Exception as e:
        raise RuntimeError(f"STT 실패: {str(e)}")