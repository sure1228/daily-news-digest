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

SUMMARY_PROMPT = """你是一位专业新闻编辑。请严格按照以下格式输出新闻汇总。

📰 YYYY年M月D日 每日新闻汇总

1. 国内要闻
标题
摘要内容（一句话说清事件要点和影响）。
标题
摘要内容。

2. 国际动态
标题
摘要内容。

3. 科技前沿
标题
摘要内容。

4. 财经市场
标题
摘要内容。

5. 社会热点
标题
摘要内容。

以上新闻来自澎湃新闻、36氪、财新网等权威媒体，精选当日重要资讯。

---
严格要求：
1. 每条新闻格式：标题 + 换行 + 摘要（一句话）
2. 分类用数字编号：1. 2. 3. 4. 5.
3. 新闻紧凑，标题简短有力
4. 总字数 800-1200 字
5. 不要开场废话，直接进入新闻
6. 确保标题和摘要都有实质内容

今日新闻内容：
{news_content}

请按上述格式输出。"""