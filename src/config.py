import os
from typing import Dict, List


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

KIMI_API_KEY = os.getenv("KIMI_API_KEY", "")
PUSHPLUS_TOKEN = os.getenv("PUSHPLUS_TOKEN", "")

AUDIO_DURATION_TARGET = 15 * 60
MAX_NEWS_PER_CATEGORY = 5
AUDIO_VOICE = "zh-CN-XiaoxiaoNeural"

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