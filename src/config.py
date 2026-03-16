import os
from typing import Dict, List


RSS_SOURCES: Dict[str, List[str]] = {
    "tech": [
        "https://36kr.com/feed",
        "https://www.huxiu.com/rss/0.xml",
        "https://rsshub.app/ithome/ranking/7days",
        "https://rsshub.app/sspai/index",
    ],
    "finance": [
        "https://rsshub.app/caixin/finance",
        "https://rsshub.app/wallstreetcn/news/global",
        "https://rsshub.app/eastmoney/report/strategyreport",
    ],
    "international": [
        "https://feeds.bbci.co.uk/zhongwen/simp/rss.xml",
        "https://rsshub.app/nyt/zh",
        "https://rsshub.app/dw/zh",
    ],
    "hot": [
        "https://rsshub.app/weibo/search/hot",
        "https://rsshub.app/zhihu/hotlist",
        "https://rsshub.app/douyin/trending",
    ],
    "general": [
        "https://rsshub.app/thepaper/featured",
        "https://rsshub.app/cls/telegraph",
        "https://rsshub.app/ifanr/latest",
    ],
}

KIMI_API_KEY = os.getenv("KIMI_API_KEY", "")
AI_API_KEY = os.getenv("AI_API_KEY", KIMI_API_KEY)
AI_PROVIDER = os.getenv("AI_PROVIDER", "kimi")
PUSHPLUS_TOKEN = os.getenv("PUSHPLUS_TOKEN", "")

AUDIO_DURATION_TARGET = 15 * 60
MAX_NEWS_PER_CATEGORY = 8
AUDIO_VOICE = "zh-CN-XiaoxiaoNeural"

SUMMARY_PROMPT = """你是一位专业新闻主播，请将今日新闻整理成一篇适合播报的文稿。

要求：
1. 总字数约 2500-3000 字（播报时长约 15 分钟）
2. 严禁使用任何形式的开头语如"好的"、"我来为您"、"让我来为您介绍"等
3. 直接进入新闻播报告阶段，立即开始新闻播报
4. 开场白：问候语 + 今日日期 + 简要预告（一句话）
5. 正文：按科技、财经、国际、热点分类播报，每条新闻用 3-4 句话详细说明（包括新闻要点、影响和背景信息）
6. 结束语：总结 + 祝福语
7. 语言风格：口语化、亲切自然、专业且生动
8. 详实度：不要一带而过，确保为听众提供有价值的新闻细节

今日新闻内容：
{news_content}

注意事项：
- 不要使用任何形式的开头语（例如："好的，这里是今天的新闻"）
- 每条新闻必须详细说明，不能简单概括
- 直接输出完整的播报告，无需额外说明"""