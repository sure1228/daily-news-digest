import asyncio
import logging
import os

import edge_tts

from src.config import AUDIO_VOICE


logger = logging.getLogger(__name__)


class TTSEngine:
    def __init__(self, voice: str = AUDIO_VOICE):
        self.voice = voice
        self.chars_per_second = 4

    async def generate_audio(self, text: str, output_path: str) -> str:
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        try:
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(output_path)
            logger.info(f"Audio saved to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to generate audio: {e}")
            raise

    def estimate_duration(self, text: str) -> int:
        clean_text = "".join(text.split())
        char_count = len(clean_text)
        return int(char_count / self.chars_per_second)

    async def generate_with_duration_check(
        self, text: str, output_path: str, target_duration: int
    ):
        estimated = self.estimate_duration(text)

        if estimated > target_duration * 1.2:
            logger.warning(
                f"Estimated duration {estimated}s exceeds target {target_duration}s"
            )

        output_path = await self.generate_audio(text, output_path)
        actual_duration = self._get_audio_duration(output_path)

        return output_path, actual_duration

    def _get_audio_duration(self, audio_path: str) -> int:
        file_size = os.path.getsize(audio_path)
        duration = int(file_size * 8 / 128000)
        return duration