import logging
from typing import List, Optional
from datetime import datetime
import requests

from src.models import NewsItem
from src.config import SUMMARY_PROMPT


logger = logging.getLogger(__name__)


class Summarizer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.moonshot.cn/v1/chat/completions"

    def generate_summary(self, news_items: List[NewsItem]) -> str:
        if not news_items:
            return "今日暂无新闻。"

        news_content = self.format_news_for_summary(news_items)

        if not self.api_key:
            logger.warning("No API key provided, returning formatted text")
            return self._format_as_broadcast(news_items)

        try:
            response = self._call_api(news_content)
            return response
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return self._format_as_broadcast(news_items)

    def format_news_for_summary(self, items: List[NewsItem]) -> str:
        sections = {}

        for item in items:
            category = self._get_category_name(item.category)
            if category not in sections:
                sections[category] = []

            text = f"标题：{item.title}"
            if item.summary:
                text += f"\n摘要：{item.summary[:200]}"
            text += f"\n来源：{item.source}\n"

            sections[category].append(text)

        output_parts = []
        for category, news_list in sections.items():
            output_parts.append(f"\n【{category}】\n")
            output_parts.extend(news_list)

        return "\n".join(output_parts)

    def _get_category_name(self, category: str) -> str:
        category_map = {
            "tech": "科技",
            "finance": "财经",
            "international": "国际",
            "hot": "热点",
            "general": "综合",
        }
        return category_map.get(category, category)

    def _format_as_broadcast(self, items: List[NewsItem]) -> str:
        lines = [
            "各位听众早上好，欢迎收听今日新闻摘要。",
            f"今天是{self._get_date_string()}。\n",
        ]

        sections = {}
        for item in items:
            cat = self._get_category_name(item.category)
            if cat not in sections:
                sections[cat] = []
            sections[cat].append(item)

        for category, news_list in sections.items():
            lines.append(f"\n下面是{category}新闻。")
            for i, item in enumerate(news_list[:5], 1):
                lines.append(f"{i}. {item.title}")
                if item.summary:
                    lines.append(f"   {item.summary[:100]}")

        lines.append("\n以上是今日新闻摘要，感谢您的收听，祝您有美好的一天！")
        return "\n".join(lines)

    def _get_date_string(self) -> str:
        now = datetime.now()
        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        return f"{now.year}年{now.month}月{now.day}日，{weekdays[now.weekday()]}"

    def _call_api(self, content: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": "moonshot-v1-8k",
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位专业的新闻主播，擅长用简洁、口语化的方式播报新闻。",
                },
                {
                    "role": "user",
                    "content": SUMMARY_PROMPT.format(news_content=content),
                },
            ],
            "temperature": 0.7,
            "max_tokens": 3000,
        }

        response = requests.post(self.api_url, headers=headers, json=data, timeout=60)
        response.raise_for_status()

        result = response.json()
        return result["choices"][0]["message"]["content"]