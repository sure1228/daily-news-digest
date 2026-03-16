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
1. 不要在文章开头使用"好的，我来为您整理"等类似开头语
2. 不添加任何解释性内容，直接进入正题
3. 每条新闻至少用 3-4 句话详细解释，包含背景、核心事实和影响
4. 保持内容准确，语言自然流畅
5. 包含开场白、正文、结束语三部分"""

        user_prompt = f"""请将以下新闻直接整理成一篇适合播报的文稿，不要添加任何额外解释说明。

新闻内容：
{content}

播报文稿要求：
- 每条新闻详细展开（3-4句话）
- 总字数 2500-3000 字
- 语言适合配音播报
- 包含开场白、新闻分类播报、结束语
- 直接输出文稿，不要任何解释"""

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
        
        # 清理AI返回的废话开头
        content = self._clean_ai_response(content)
        logger.info(f"After cleaning, content length: {len(content)} characters")
        
        return content
    
    def _clean_ai_response(self, text: str) -> str:
        """
        清理AI返回内容中不必要的说明文字、客气话等
        """
        # 常见的需要移除的开头语句
        prefixes_to_remove = [
            "好的，",
            "好的。", 
            "好的，我",
            "我来", 
            "让我",
            "好的，接下来", 
            "您好，",
            "你好，",
            "您好！",
            "你好！",
            "根据您的要求",
            "以下是今天的",
            "这是今天的",
            "这里是今天的"
        ]
        
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # 移除前导空白
            striped_line = line.strip()
            if not striped_line:
                cleaned_lines.append(line)  # 保留空行用于格式
                continue
                
            # 检查是否以需要移除的前缀开头
            skip_line = False
            for prefix in prefixes_to_remove:
                if striped_line.startswith(prefix):
                    # 如果这个句子较短（小于20个字符），则跳过
                    if len(striped_line) < 20:
                        skip_line = True
                        break
            
            if not skip_line:
                cleaned_lines.append(line)
        
        # 重新组合文本
        cleaned_text = '\n'.join(cleaned_lines)
        
        # 移除开头可能存在的废话段落
        paragraphs = cleaned_text.split('\n\n')
        final_paragraphs = []
        
        for paragraph in paragraphs:
            # 检查段落是否是开头废话
            is_intro_comment = any(paragraph.strip().startswith(prefix) and len(paragraph.strip()) < 50 
                                 for prefix in prefixes_to_remove)
            
            if not is_intro_comment:
                final_paragraphs.append(paragraph)
            else:
                # 如果该段落看起来只是客套话，则跳过
                continue
        
        return '\n\n'.join(final_paragraphs)