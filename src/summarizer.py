import logging
from typing import List
from datetime import datetime
import os
import requests

from src.models import NewsItem
from src.config import SUMMARY_PROMPT


logger = logging.getLogger(__name__)

AI_PROVIDERS = {
    "kimi": {
        "url": "https://api.moonshot.cn/v1/chat/completions",
        "model": "moonshot-v1-32k",
    },
    "qwen": {
        "url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        "model": "qwen-turbo",
    },
    "qwen-plus": {
        "url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        "model": "qwen-plus",
    },
    "deepseek": {
        "url": "https://api.deepseek.com/v1/chat/completions",
        "model": "deepseek-chat",
    },
    "openai": {
        "url": "https://api.openai.com/v1/chat/completions",
        "model": "gpt-3.5-turbo",
    },
}


class Summarizer:
    def __init__(self, api_key: str, provider: str = "kimi"):
        self.api_key = api_key
        self.provider = provider.lower() if provider else "kimi"

        if self.provider in AI_PROVIDERS:
            self.api_url = AI_PROVIDERS[self.provider]["url"]
            self.model = AI_PROVIDERS[self.provider]["model"]
        else:
            self.api_url = AI_PROVIDERS["kimi"]["url"]
            self.model = AI_PROVIDERS["kimi"]["model"]

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
            logger.error(f"Failed to generate summary with {self.provider}: {e}")
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

        system_prompt = """你是一位专业新闻主播。你的任务是将新闻整理成适合音频播报的文稿。

重要要求：
1. 必须输出 2500-3000 字的完整文稿
2. 不要中途停止，必须完成全部内容
3. 每条新闻至少用 3-4 句话详细解释
4. 包含开场白、正文、结束语三部分"""

        user_prompt = f"""请将以下新闻整理成一篇 2500-3000 字的播报文稿。

{SUMMARY_PROMPT.format(news_content=content)}

记住：必须输出完整文稿，字数不能少于 2500 字！"""

        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 4096,
        }

        logger.info(f"Calling {self.provider} API with model {self.model}")
        response = requests.post(self.api_url, headers=headers, json=data, timeout=180)
        response.raise_for_status()

        result = response.json()
        
        if "choices" not in result:
            logger.error(f"API response missing choices: {result}")
            raise ValueError("Invalid API response")
        
        content = result["choices"][0]["message"]["content"]
        logger.info(f"API returned {len(content)} characters, {result.get('usage', {})}")
        
        return content