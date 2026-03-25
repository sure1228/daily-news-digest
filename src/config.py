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
        "https://rsshub.app/cls/telegraph",
    ],
    "international": [
        "https://feeds.bbci.co.uk/zhongwen/simp/rss.xml",
        "https://rsshub.app/nyt/zh",
        "https://rsshub.app/dw/zh",
        "https://rsshub.app/voa/chinese",
    ],
    "hot": [
        "https://rsshub.app/weibo/search/hot",
        "https://rsshub.app/zhihu/hotlist",
        "https://rsshub.app/douyin/trending",
        "https://rsshub.app/baidu/topwords",
    ],
    "general": [
        "https://rsshub.app/thepaper/featured",
        "https://rsshub.app/caixin/weekly",
    ],
    "social": [
        "https://rsshub.app/toutiao/hot",
        "https://rsshub.app/xiaohongshu/hot",
    ],
    "tech-community": [
        "https://rsshub.app/github/trending/daily",
    ],
}

KIMI_API_KEY = os.getenv("KIMI_API_KEY", "")
AI_API_KEY = os.getenv("AI_API_KEY", KIMI_API_KEY)
AI_PROVIDER = os.getenv("AI_PROVIDER", "kimi")
PUSHPLUS_TOKEN = os.getenv("PUSHPLUS_TOKEN", "")

AUDIO_DURATION_TARGET = 8 * 60
MAX_NEWS_PER_CATEGORY = 6
MIN_TOTAL_NEWS = 20
AUDIO_VOICE = "zh-CN-XiaoxiaoNeural"

SUMMARY_PROMPT = """你是一位专业新闻主播。请严格按照以下格式输出播报文稿。

【开场】
早上好，今天是X月X日，周X。今天要关注：[一句话预告3个重点]

【科技】

• [标题1] 内容。背景。影响。
• [标题2] 内容。背景。影响。

【财经】

• [标题] 内容。背景。影响。

【国际】

• [标题] 内容。背景。影响。

【热点】

• [标题] 内容。背景。影响。

【结束语】
今天最重要的新闻是[X]。[一句深度思考或展望，不要"感谢收听"等套话]

---
严格要求：
1. 每条新闻格式：• [标题] 内容(2-3句)。保持一致
2. 每条新闻独立一行，不要合并
3. 分类之间空一行
4. 总字数 1000-1500 字
5. 不要开头废话，直接进入开场
6. 结束语不要套话

今日新闻内容：
{news_content}

请按上述格式输出。"""