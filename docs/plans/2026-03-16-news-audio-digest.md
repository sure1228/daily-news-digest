# 新闻音频摘要系统实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use the `skill` tool with `name="superpowers/executing-plans"` to implement this plan task-by-task.

**Goal:** 构建每天早上自动抓取新闻、生成 15 分钟音频摘要、推送到微信的自动化系统。

**Architecture:** Python 脚本 + GitHub Actions 定时执行。RSS 抓取 → AI 摘要 → Edge TTS 语音合成 → Pushplus 微信推送。

**Tech Stack:** Python 3.11, feedparser, edge-tts, Kimi API, Pushplus API, GitHub Actions

---

## Task 1: 项目初始化

**Files:**
- Create: `requirements.txt`
- Create: `src/__init__.py`
- Create: `.gitignore`
- Create: `output/.gitkeep`

**Step 1: 创建项目目录结构**

```bash
mkdir -p src output .github/workflows tests
```

**Step 2: 创建 requirements.txt**

```txt
feedparser>=6.0.0
edge-tts>=6.1.0
requests>=2.28.0
python-dotenv>=1.0.0
pytest>=7.0.0
pytest-asyncio>=0.21.0
```

**Step 3: 创建 .gitignore**

```
__pycache__/
*.py[cod]
.env
output/*.mp3
output/*.txt
.pytest_cache/
.venv/
```

**Step 4: 创建 src/__init__.py**

```python
"""新闻音频摘要系统"""
__version__ = "0.1.0"
```

**Step 5: 创建 output/.gitkeep**

```bash
touch output/.gitkeep
```

**Step 6: 提交**

```bash
git add .
git commit -m "chore: initialize project structure"
```

---

## Task 2: 配置模块

**Files:**
- Create: `src/config.py`
- Create: `tests/test_config.py`

**Step 1: 编写测试**

```python
# tests/test_config.py
import os
from src.config import RSS_SOURCES, MAX_NEWS_PER_CATEGORY, AUDIO_DURATION_TARGET


def test_rss_sources_not_empty():
    """测试 RSS 源配置不为空"""
    assert len(RSS_SOURCES) > 0


def test_each_category_has_sources():
    """测试每个类别至少有一个源"""
    for category, sources in RSS_SOURCES.items():
        assert len(sources) > 0, f"Category {category} has no sources"


def test_max_news_default():
    """测试默认每类新闻数量"""
    assert MAX_NEWS_PER_CATEGORY == 5


def test_audio_duration_default():
    """测试默认音频时长"""
    assert AUDIO_DURATION_TARGET == 15 * 60
```

**Step 2: 运行测试验证失败**

```bash
python -m pytest tests/test_config.py -v
```
Expected: FAIL (config module not found)

**Step 3: 实现配置模块**

```python
# src/config.py
"""系统配置"""
import os
from typing import Dict, List


# 新闻源配置
RSS_SOURCES: Dict[str, List[str]] = {
    "tech": [
        "https://36kr.com/feed",
        "https://www.huxiu.com/rss/0.xml",
        "https://www.geekpark.net/rss",
    ],
    "finance": [
        "https://rsshub.app/caixin/finance",
        "https://rsshub.app/wallstreetcn/news/global",
    ],
    "international": [
        "https://feeds.bbci.co.uk/zhongwen/simp/rss.xml",
        "https://cn.reuters.com/rssFeed/worldNews",
    ],
    "hot": [
        "https://rsshub.app/weibo/search/hot",
        "https://rsshub.app/zhihu/daily",
    ],
    "general": [
        "https://rsshub.app/thepaper/featured",
        "https://www.jiemian.com/rss/news.xml",
    ],
}

# API 配置 (从环境变量读取)
KIMI_API_KEY = os.getenv("KIMI_API_KEY", "")
PUSHPLUS_TOKEN = os.getenv("PUSHPLUS_TOKEN", "")

# 输出配置
AUDIO_DURATION_TARGET = 15 * 60  # 15 分钟 (秒)
MAX_NEWS_PER_CATEGORY = 5
AUDIO_VOICE = "zh-CN-XiaoxiaoNeural"  # Edge TTS 中文女声

# 提示词模板
SUMMARY_PROMPT = """你是一位新闻主播，请用口语化的方式总结今天的新闻。

要求：
1. 总时长控制在 15 分钟左右（约 2500 字）
2. 使用播报风格，有开场白和结束语
3. 分类播报：科技、财经、国际、热点
4. 每条新闻用 2-3 句话概括要点
5. 语气轻松但不失专业

今日新闻内容：
{news_content}
"""
```

**Step 4: 运行测试验证通过**

```bash
python -m pytest tests/test_config.py -v
```
Expected: PASS

**Step 5: 提交**

```bash
git add src/config.py tests/test_config.py
git commit -m "feat: add configuration module"
```

---

## Task 3: 数据模型

**Files:**
- Create: `src/models.py`
- Create: `tests/test_models.py`

**Step 1: 编写测试**

```python
# tests/test_models.py
from datetime import datetime
from src.models import NewsItem


def test_news_item_creation():
    """测试新闻条目创建"""
    item = NewsItem(
        title="测试新闻",
        link="https://example.com",
        summary="这是摘要",
        category="tech",
        source="测试源",
    )
    assert item.title == "测试新闻"
    assert item.category == "tech"


def test_news_item_published_time():
    """测试发布时间字段"""
    now = datetime.now()
    item = NewsItem(
        title="测试",
        link="https://example.com",
        category="tech",
        source="测试",
        published=now,
    )
    assert item.published == now


def test_news_item_to_dict():
    """测试转换为字典"""
    item = NewsItem(
        title="测试",
        link="https://example.com",
        summary="摘要",
        category="tech",
        source="源",
    )
    d = item.to_dict()
    assert d["title"] == "测试"
    assert d["link"] == "https://example.com"
```

**Step 2: 运行测试验证失败**

```bash
python -m pytest tests/test_models.py -v
```
Expected: FAIL (models module not found)

**Step 3: 实现数据模型**

```python
# src/models.py
"""数据模型"""
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


@dataclass
class NewsItem:
    """新闻条目"""
    title: str
    link: str
    category: str
    source: str
    summary: str = ""
    published: Optional[datetime] = None

    def to_dict(self) -> dict:
        """转换为字典"""
        return asdict(self)


@dataclass
class DigestResult:
    """摘要结果"""
    date: str
    title: str
    summary_text: str
    audio_path: str
    audio_duration: float = 0.0
    news_count: int = 0
```

**Step 4: 运行测试验证通过**

```bash
python -m pytest tests/test_models.py -v
```
Expected: PASS

**Step 5: 提交**

```bash
git add src/models.py tests/test_models.py
git commit -m "feat: add data models"
```

---

## Task 4: 新闻抓取器 - RSS 解析

**Files:**
- Create: `src/fetcher.py`
- Create: `tests/test_fetcher.py`

**Step 1: 编写测试**

```python
# tests/test_fetcher.py
import pytest
from src.fetcher import NewsFetcher
from src.models import NewsItem


class TestNewsFetcher:
    def test_fetch_rss_returns_list(self):
        """测试 RSS 抓取返回列表"""
        fetcher = NewsFetcher()
        # 使用一个稳定的测试 RSS 源
        items = fetcher.fetch_rss("https://feeds.bbci.co.uk/zhongwen/simp/rss.xml")
        assert isinstance(items, list)

    def test_fetch_rss_items_have_required_fields(self):
        """测试返回的条目包含必要字段"""
        fetcher = NewsFetcher()
        items = fetcher.fetch_rss("https://feeds.bbci.co.uk/zhongwen/simp/rss.xml")
        if items:  # 如果有返回
            item = items[0]
            assert item.title
            assert item.link
            assert item.category

    def test_deduplicate_removes_duplicates(self):
        """测试去重功能"""
        fetcher = NewsFetcher()
        items = [
            NewsItem(title="相同标题", link="https://a.com", category="tech", source="A"),
            NewsItem(title="相同标题", link="https://b.com", category="tech", source="B"),
            NewsItem(title="不同标题", link="https://c.com", category="tech", source="C"),
        ]
        deduped = fetcher.deduplicate(items)
        assert len(deduped) == 2

    def test_fetch_all_categories(self):
        """测试抓取所有类别"""
        fetcher = NewsFetcher()
        # 只测试一个源以节省时间
        sources = {"tech": ["https://36kr.com/feed"]}
        items = fetcher.fetch_all(sources, max_per_category=2)
        assert isinstance(items, list)
```

**Step 2: 运行测试验证失败**

```bash
python -m pytest tests/test_fetcher.py -v
```
Expected: FAIL (fetcher module not found)

**Step 3: 实现新闻抓取器**

```python
# src/fetcher.py
"""新闻抓取器"""
import logging
from typing import List, Dict
from datetime import datetime
import feedparser

from src.models import NewsItem
from src.config import MAX_NEWS_PER_CATEGORY


logger = logging.getLogger(__name__)


class NewsFetcher:
    """新闻抓取器"""

    def fetch_rss(self, url: str, category: str = "general") -> List[NewsItem]:
        """抓取单个 RSS 源"""
        items = []
        try:
            feed = feedparser.parse(url)
            source_name = feed.feed.get("title", url)

            for entry in feed.entries[:10]:  # 每个源最多 10 条
                item = NewsItem(
                    title=entry.get("title", "无标题"),
                    link=entry.get("link", ""),
                    summary=entry.get("summary", ""),
                    category=category,
                    source=source_name,
                    published=self._parse_published(entry),
                )
                items.append(item)
        except Exception as e:
            logger.error(f"Failed to fetch RSS {url}: {e}")

        return items

    def _parse_published(self, entry) -> datetime:
        """解析发布时间"""
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            return datetime(*entry.published_parsed[:6])
        return datetime.now()

    def fetch_all(
        self, sources: Dict[str, List[str]], max_per_category: int = MAX_NEWS_PER_CATEGORY
    ) -> List[NewsItem]:
        """抓取所有源"""
        all_items = []

        for category, urls in sources.items():
            category_items = []
            for url in urls:
                items = self.fetch_rss(url, category)
                category_items.extend(items)

            # 每个类别限制数量
            all_items.extend(category_items[:max_per_category])

        return self.deduplicate(all_items)

    def deduplicate(self, items: List[NewsItem]) -> List[NewsItem]:
        """根据标题去重"""
        seen_titles = set()
        unique_items = []

        for item in items:
            # 标准化标题进行比较
            normalized_title = item.title.strip().lower()
            if normalized_title not in seen_titles:
                seen_titles.add(normalized_title)
                unique_items.append(item)

        return unique_items
```

**Step 4: 运行测试验证通过**

```bash
python -m pytest tests/test_fetcher.py -v
```
Expected: PASS (部分测试可能因为网络原因需要重试)

**Step 5: 提交**

```bash
git add src/fetcher.py tests/test_fetcher.py
git commit -m "feat: add news fetcher with RSS parsing"
```

---

## Task 5: AI 摘要生成器

**Files:**
- Create: `src/summarizer.py`
- Create: `tests/test_summarizer.py`

**Step 1: 编写测试**

```python
# tests/test_summarizer.py
import pytest
from src.summarizer import Summarizer
from src.models import NewsItem


class TestSummarizer:
    def test_format_news_for_summary(self):
        """测试新闻格式化"""
        summarizer = Summarizer("test_key")
        items = [
            NewsItem(
                title="测试标题1",
                link="https://a.com",
                summary="摘要1",
                category="tech",
                source="源A",
            ),
            NewsItem(
                title="测试标题2",
                link="https://b.com",
                summary="摘要2",
                category="finance",
                source="源B",
            ),
        ]
        formatted = summarizer.format_news_for_summary(items)
        assert "测试标题1" in formatted
        assert "测试标题2" in formatted
        assert "科技" in formatted or "tech" in formatted.lower()

    def test_generate_summary_without_api_key(self):
        """测试无 API Key 时的处理"""
        summarizer = Summarizer("")
        items = [
            NewsItem(
                title="测试",
                link="https://a.com",
                category="tech",
                source="测试源",
            )
        ]
        # 无 API Key 时应该返回格式化的文本
        result = summarizer.generate_summary(items)
        assert result  # 应该有返回值
```

**Step 2: 运行测试验证失败**

```bash
python -m pytest tests/test_summarizer.py -v
```
Expected: FAIL (summarizer module not found)

**Step 3: 实现摘要生成器**

```python
# src/summarizer.py
"""AI 摘要生成器"""
import logging
from typing import List, Optional
import requests

from src.models import NewsItem
from src.config import SUMMARY_PROMPT


logger = logging.getLogger(__name__)


class Summarizer:
    """AI 摘要生成器 (使用 Kimi API)"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.moonshot.cn/v1/chat/completions"

    def generate_summary(self, news_items: List[NewsItem]) -> str:
        """生成新闻摘要"""
        if not news_items:
            return "今日暂无新闻。"

        # 格式化新闻内容
        news_content = self.format_news_for_summary(news_items)

        # 如果没有 API Key，返回格式化的文本
        if not self.api_key:
            logger.warning("No API key provided, returning formatted text")
            return self._format_as_broadcast(news_items)

        # 调用 Kimi API
        try:
            response = self._call_api(news_content)
            return response
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return self._format_as_broadcast(news_items)

    def format_news_for_summary(self, items: List[NewsItem]) -> str:
        """格式化新闻内容供 AI 处理"""
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

        # 组装输出
        output_parts = []
        for category, news_list in sections.items():
            output_parts.append(f"\n【{category}】\n")
            output_parts.extend(news_list)

        return "\n".join(output_parts)

    def _get_category_name(self, category: str) -> str:
        """获取类别中文名"""
        category_map = {
            "tech": "科技",
            "finance": "财经",
            "international": "国际",
            "hot": "热点",
            "general": "综合",
        }
        return category_map.get(category, category)

    def _format_as_broadcast(self, items: List[NewsItem]) -> str:
        """格式化为播报文本"""
        lines = [
            "各位听众早上好，欢迎收听今日新闻摘要。",
            "今天是" + self._get_date_string() + "。\n",
        ]

        # 按类别分组
        sections = {}
        for item in items:
            cat = self._get_category_name(item.category)
            if cat not in sections:
                sections[cat] = []
            sections[cat].append(item)

        # 生成各部分
        for category, news_list in sections.items():
            lines.append(f"\n下面是{category}新闻。")
            for i, item in enumerate(news_list[:5], 1):
                lines.append(f"{i}. {item.title}")
                if item.summary:
                    lines.append(f"   {item.summary[:100]}")

        lines.append("\n以上是今日新闻摘要，感谢您的收听，祝您有美好的一天！")
        return "\n".join(lines)

    def _get_date_string(self) -> str:
        """获取日期字符串"""
        from datetime import datetime
        now = datetime.now()
        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        return f"{now.year}年{now.month}月{now.day}日，{weekdays[now.weekday()]}"

    def _call_api(self, content: str) -> str:
        """调用 Kimi API"""
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
```

**Step 4: 运行测试验证通过**

```bash
python -m pytest tests/test_summarizer.py -v
```
Expected: PASS

**Step 5: 提交**

```bash
git add src/summarizer.py tests/test_summarizer.py
git commit -m "feat: add AI summarizer with Kimi API support"
```

---

## Task 6: 语音合成引擎

**Files:**
- Create: `src/tts.py`
- Create: `tests/test_tts.py`

**Step 1: 编写测试**

```python
# tests/test_tts.py
import pytest
import os
from src.tts import TTSEngine


class TestTTSEngine:
    @pytest.mark.asyncio
    async def test_estimate_duration(self):
        """测试时长估算"""
        engine = TTSEngine()
        # 中文平均语速约 4 字/秒
        text = "这是一段测试文本" * 100  # 800 字
        duration = engine.estimate_duration(text)
        # 预估约 200 秒 (800/4)
        assert 150 < duration < 250

    @pytest.mark.asyncio
    async def test_generate_audio(self):
        """测试音频生成"""
        engine = TTSEngine()
        output_path = "output/test_audio.mp3"

        # 确保输出目录存在
        os.makedirs("output", exist_ok=True)

        # 生成音频
        text = "这是测试音频生成。"
        result = await engine.generate_audio(text, output_path)

        # 检查文件是否创建
        assert os.path.exists(result)

        # 清理测试文件
        if os.path.exists(result):
            os.remove(result)
```

**Step 2: 运行测试验证失败**

```bash
python -m pytest tests/test_tts.py -v
```
Expected: FAIL (tts module not found)

**Step 3: 实现 TTS 引擎**

```python
# src/tts.py
"""语音合成引擎"""
import asyncio
import logging
import os
from pathlib import Path

import edge_tts

from src.config import AUDIO_VOICE


logger = logging.getLogger(__name__)


class TTSEngine:
    """Edge TTS 语音合成引擎"""

    def __init__(self, voice: str = AUDIO_VOICE):
        self.voice = voice
        # 中文平均语速：约 4 字/秒
        self.chars_per_second = 4

    async def generate_audio(self, text: str, output_path: str) -> str:
        """生成音频文件"""
        # 确保输出目录存在
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
        """估算音频时长（秒）"""
        # 移除空白字符
        clean_text = "".join(text.split())
        char_count = len(clean_text)
        # 估算时长
        return int(char_count / self.chars_per_second)

    async def generate_with_duration_check(
        self, text: str, output_path: str, target_duration: int
    ) -> tuple[str, int]:
        """生成音频并检查时长"""
        # 估算是否需要截断
        estimated = self.estimate_duration(text)

        if estimated > target_duration * 1.2:  # 超过目标 20%
            logger.warning(
                f"Estimated duration {estimated}s exceeds target {target_duration}s"
            )
            # 可以在这里添加截断逻辑

        output_path = await self.generate_audio(text, output_path)

        # 获取实际时长
        actual_duration = self._get_audio_duration(output_path)

        return output_path, actual_duration

    def _get_audio_duration(self, audio_path: str) -> int:
        """获取音频实际时长"""
        # 简单实现：使用估算值
        # 更精确的实现可以使用 mutagen 或 ffmpeg
        file_size = os.path.getsize(audio_path)
        # MP3 比特率估算 (约 128kbps)
        duration = int(file_size * 8 / 128000)
        return duration
```

**Step 4: 运行测试验证通过**

```bash
python -m pytest tests/test_tts.py -v
```
Expected: PASS

**Step 5: 提交**

```bash
git add src/tts.py tests/test_tts.py
git commit -m "feat: add TTS engine with Edge TTS"
```

---

## Task 7: 微信推送服务

**Files:**
- Create: `src/pusher.py`
- Create: `tests/test_pusher.py`

**Step 1: 编写测试**

```python
# tests/test_pusher.py
import pytest
from unittest.mock import patch, Mock
from src.pusher import WeChatPusher


class TestWeChatPusher:
    def test_init_with_token(self):
        """测试初始化"""
        pusher = WeChatPusher("test_token")
        assert pusher.token == "test_token"

    @patch("src.pusher.requests.post")
    def test_send_success(self, mock_post):
        """测试发送成功"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"code": 200}
        mock_post.return_value = mock_response

        pusher = WeChatPusher("test_token")
        result = pusher.send(
            title="测试标题",
            content="测试内容",
            audio_url="https://example.com/audio.mp3",
        )

        assert result is True
        mock_post.assert_called_once()

    @patch("src.pusher.requests.post")
    def test_send_failure(self, mock_post):
        """测试发送失败"""
        mock_post.side_effect = Exception("Network error")

        pusher = WeChatPusher("test_token")
        result = pusher.send(
            title="测试标题",
            content="测试内容",
            audio_url="https://example.com/audio.mp3",
        )

        assert result is False

    def test_format_message(self):
        """测试消息格式化"""
        pusher = WeChatPusher("test_token")
        message = pusher._format_message(
            title="今日新闻",
            content="新闻内容",
            audio_url="https://example.com/audio.mp3",
        )

        assert "今日新闻" in message["title"]
        assert "新闻内容" in message["content"]
        assert "https://example.com/audio.mp3" in message["content"]
```

**Step 2: 运行测试验证失败**

```bash
python -m pytest tests/test_pusher.py -v
```
Expected: FAIL (pusher module not found)

**Step 3: 实现推送服务**

```python
# src/pusher.py
"""微信推送服务"""
import logging
from typing import Optional

import requests


logger = logging.getLogger(__name__)


class WeChatPusher:
    """Pushplus 微信推送"""

    API_URL = "http://www.pushplus.plus/send"

    def __init__(self, token: str):
        self.token = token

    def send(
        self,
        title: str,
        content: str,
        audio_url: Optional[str] = None,
    ) -> bool:
        """发送消息到微信"""
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
        """格式化消息"""
        # 构建内容
        full_content = content

        if audio_url:
            full_content += f"\n\n🎧 [点击收听音频]({audio_url})"

        return {
            "token": self.token,
            "title": title,
            "content": full_content,
            "template": "markdown",
        }
```

**Step 4: 运行测试验证通过**

```bash
python -m pytest tests/test_pusher.py -v
```
Expected: PASS

**Step 5: 提交**

```bash
git add src/pusher.py tests/test_pusher.py
git commit -m "feat: add WeChat pusher with Pushplus"
```

---

## Task 8: 主程序入口

**Files:**
- Create: `main.py`

**Step 1: 创建主程序**

```python
#!/usr/bin/env python3
"""新闻音频摘要系统主程序"""
import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from src.config import RSS_SOURCES, KIMI_API_KEY, PUSHPLUS_TOKEN, AUDIO_DURATION_TARGET
from src.fetcher import NewsFetcher
from src.summarizer import Summarizer
from src.tts import TTSEngine
from src.pusher import WeChatPusher
from src.models import DigestResult


# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    """主程序"""
    logger.info("Starting daily news digest...")

    # 1. 抓取新闻
    logger.info("Fetching news...")
    fetcher = NewsFetcher()
    news_items = fetcher.fetch_all(RSS_SOURCES)
    logger.info(f"Fetched {len(news_items)} news items")

    if not news_items:
        logger.warning("No news items fetched, exiting")
        return

    # 2. 生成摘要
    logger.info("Generating summary...")
    summarizer = Summarizer(os.getenv("KIMI_API_KEY", KIMI_API_KEY))
    summary = summarizer.generate_summary(news_items)
    logger.info(f"Summary generated: {len(summary)} characters")

    # 3. 生成音频
    logger.info("Generating audio...")
    tts = TTSEngine()

    # 生成输出路径
    today = datetime.now().strftime("%Y-%m-%d")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    audio_path = str(output_dir / f"news-{today}.mp3")

    try:
        audio_path = await tts.generate_audio(summary, audio_path)
        logger.info(f"Audio generated: {audio_path}")
    except Exception as e:
        logger.error(f"Failed to generate audio: {e}")
        audio_path = None

    # 4. 推送到微信
    logger.info("Pushing to WeChat...")
    pusher = WeChatPusher(os.getenv("PUSHPLUS_TOKEN", PUSHPLUS_TOKEN))

    title = f"📰 今日新闻摘要 - {today}"
    audio_url = None  # 如果有公网访问，可以设置音频 URL

    success = pusher.send(
        title=title,
        content=summary[:500] + "\n\n..." if len(summary) > 500 else summary,
        audio_url=audio_url,
    )

    if success:
        logger.info("Push successful")
    else:
        logger.warning("Push failed")

    # 5. 保存结果
    result = DigestResult(
        date=today,
        title=title,
        summary_text=summary,
        audio_path=audio_path or "",
        news_count=len(news_items),
    )

    # 保存摘要文本
    text_path = output_dir / f"summary-{today}.txt"
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(summary)
    logger.info(f"Summary saved to {text_path}")

    logger.info("Daily news digest completed!")
    return result


if __name__ == "__main__":
    asyncio.run(main())
```

**Step 2: 提交**

```bash
git add main.py
git commit -m "feat: add main program entry point"
```

---

## Task 9: GitHub Actions 工作流

**Files:**
- Create: `.github/workflows/daily-news.yml`

**Step 1: 创建工作流文件**

```yaml
# .github/workflows/daily-news.yml
name: Daily News Audio Digest

on:
  schedule:
    # 每天 UTC 0:00 运行 (北京时间 8:00)
    - cron: '0 0 * * *'
  workflow_dispatch:  # 支持手动触发

jobs:
  generate-digest:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run news digest
        env:
          KIMI_API_KEY: ${{ secrets.KIMI_API_KEY }}
          PUSHPLUS_TOKEN: ${{ secrets.PUSHPLUS_TOKEN }}
        run: python main.py

      - name: Upload audio artifact
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: daily-audio-${{ github.run_number }}
          path: output/
          retention-days: 7

      - name: Commit audio file
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add output/*.mp3 output/*.txt || true
          git diff --quiet && git diff --staged --quiet || git commit -m "chore: add daily audio digest"
          git push || true
```

**Step 2: 提交**

```bash
git add .github/workflows/daily-news.yml
git commit -m "feat: add GitHub Actions workflow"
```

---

## Task 10: README 文档

**Files:**
- Create: `README.md`

**Step 1: 创建 README**

```markdown
# 📰 每日新闻音频摘要

每天早上 8:00 自动抓取多元化新闻，生成 15 分钟中文音频摘要，推送到微信。

## 功能特点

- 🔄 **全自动**：GitHub Actions 定时执行，无需本地运行
- 📻 **音频播报**：15 分钟中文语音，通勤路上听新闻
- 📱 **微信推送**：通过 Pushplus 推送到微信，无需安装 App
- 🌐 **多元新闻源**：科技、财经、国际、热点，避免信息茧房
- 💰 **完全免费**：所有服务使用免费额度

## 快速开始

### 1. Fork 本仓库

点击右上角 Fork 按钮。

### 2. 获取 API Keys

| 服务 | 获取方式 | 用途 |
|------|----------|------|
| Kimi API | https://platform.moonshot.cn/ | AI 摘要生成 |
| Pushplus | https://www.pushplus.plus/ | 微信推送 |

### 3. 配置 Secrets

在 Fork 的仓库中：
1. 进入 Settings → Secrets and variables → Actions
2. 添加以下 Secrets：
   - `KIMI_API_KEY`：Kimi API 密钥
   - `PUSHPLUS_TOKEN`：Pushplus Token

### 4. 启用 GitHub Actions

1. 进入 Actions 标签页
2. 点击 "I understand my workflows, go ahead and enable them"

### 5. 测试运行

1. 进入 Actions → Daily News Audio Digest
2. 点击 "Run workflow" → "Run workflow"
3. 等待执行完成，检查微信是否收到消息

## 新闻来源

| 分类 | 来源 |
|------|------|
| 科技 | 36氪、虎嗅、极客公园 |
| 财经 | 财新网、华尔街见闻 |
| 国际 | BBC 中文、路透社 |
| 热点 | 微博热搜、知乎日报 |
| 综合 | 澎湃新闻、界面新闻 |

## 自定义

### 修改新闻源

编辑 `src/config.py` 中的 `RSS_SOURCES`：

```python
RSS_SOURCES = {
    "tech": ["https://your-rss-feed.com/feed"],
    # ...
}
```

### 修改推送时间

编辑 `.github/workflows/daily-news.yml` 中的 cron 表达式：

```yaml
schedule:
  - cron: '0 0 * * *'  # UTC 时间，北京时间需要 +8
```

### 修改语音

编辑 `src/config.py` 中的 `AUDIO_VOICE`：

```python
AUDIO_VOICE = "zh-CN-YunxiNeural"  # 男声
```

可选语音：
- `zh-CN-XiaoxiaoNeural`：女声（默认）
- `zh-CN-YunxiNeural`：男声
- `zh-CN-YunjianNeural`：新闻男声

## 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export KIMI_API_KEY="your_key"
export PUSHPLUS_TOKEN="your_token"

# 运行
python main.py
```

## 项目结构

```
daily-news-digest/
├── .github/workflows/    # GitHub Actions 工作流
├── src/                  # 源代码
│   ├── config.py         # 配置
│   ├── fetcher.py        # 新闻抓取
│   ├── summarizer.py     # AI 摘要
│   ├── tts.py            # 语音合成
│   └── pusher.py         # 推送服务
├── output/               # 输出文件
├── tests/                # 测试
├── main.py               # 主程序
└── requirements.txt      # 依赖
```

## License

MIT
```

**Step 2: 提交**

```bash
git add README.md
git commit -m "docs: add README"
```

---

## Task 11: 最终验证

**Step 1: 运行所有测试**

```bash
python -m pytest tests/ -v
```
Expected: All tests PASS

**Step 2: 本地测试运行**

```bash
# 创建 .env 文件
cat > .env << EOF
KIMI_API_KEY=your_key_here
PUSHPLUS_TOKEN=your_token_here
EOF

# 运行（不需要真实 API Key，会降级为本地模式）
python main.py
```
Expected: 程序成功运行并生成 output/news-*.mp3

**Step 3: 提交最终版本**

```bash
git add .
git commit -m "chore: final cleanup and verification"
```

---

## 执行完成检查清单

- [ ] 所有测试通过
- [ ] 本地运行成功生成音频
- [ ] GitHub Actions 工作流配置正确
- [ ] README 文档完整
- [ ] .gitignore 排除了敏感文件