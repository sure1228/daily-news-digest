import logging
from typing import Optional

import requests


logger = logging.getLogger(__name__)


class WeChatPusher:
    API_URL = "http://www.pushplus.plus/send"

    def __init__(self, token: str):
        self.token = token

    def send(
        self,
        title: str,
        content: str,
        audio_url: Optional[str] = None,
    ) -> bool:
        if not self.token:
            logger.warning("No Pushplus token provided, skipping push")
            return False

        message = self._format_message(title, content, audio_url)

        try:
            response = requests.post(
                self.API_URL,
                json=message,
                timeout=30,
            )
            result = response.json()

            if result.get("code") == 200:
                logger.info("Message sent successfully")
                return True
            else:
                logger.error(f"Failed to send message: {result}")
                return False

        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False

    def _format_message(
        self,
        title: str,
        content: str,
        audio_url: Optional[str],
    ) -> dict:
        full_content = content

        if audio_url:
            full_content += f"\n\n🎧 [点击收听音频]({audio_url})"

        return {
            "token": self.token,
            "title": title,
            "content": full_content,
            "template": "markdown",
        }