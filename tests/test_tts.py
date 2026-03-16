import os
import pytest
from src.tts import TTSEngine


class TestTTSEngine:
    def test_estimate_duration(self):
        engine = TTSEngine()
        text = "这是一段测试文本" * 100
        duration = engine.estimate_duration(text)
        assert 150 < duration < 250

    @pytest.mark.asyncio
    async def test_generate_audio(self):
        engine = TTSEngine()
        output_path = "output/test_audio.mp3"

        os.makedirs("output", exist_ok=True)

        text = "这是测试音频生成。"
        result = await engine.generate_audio(text, output_path)

        assert os.path.exists(result)

        if os.path.exists(result):
            os.remove(result)