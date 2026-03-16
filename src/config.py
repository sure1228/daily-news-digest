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
2. 开场白：问候语 + 今日日期 + 简要预告
3. 正文：按科技、财经、国际、热点分类播报，每条新闻用 2-3 句话概括要点，注意新闻之间的过渡要自然
4. 结束语：总结 + 祝福语
5. 语言风格：口语化、亲切自然、专业但不枯燥

今日新闻内容：
{news_content}

请直接输出播报文稿，不要有任何解释或说明。"""