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

SUMMARY_PROMPT = """你是一位专业新闻主播，请将今日新闻整理成一篇适合播报的文稿。

格式要求：
1. 每条新闻使用独立的 bullet point（•）标记
2. 格式：• [新闻标题] 新闻详细内容（2-3句话）
3. 分类之间用空行分隔

内容要求：
1. 总字数约 1000-1500 字（播报时长约 6-8 分钟）
2. 严禁使用任何形式的开头语如"好的"、"我来为您"等
3. 每条新闻说明：要点 + 一句背景或影响
4. 信息密度要高，不要废话

结构：
- 开场：问候 + 今天日期 + 今日要闻预告（一句话）
- 正文：分类播报，每条新闻一个 bullet point
- 结束语：
  - 回顾今日最重要的新闻事件
  - 一句有深度的思考或展望
  - 禁止使用"感谢收听"等套话

今日新闻内容：
{news_content}

直接输出播报文稿，每条新闻用 • 开头。"""