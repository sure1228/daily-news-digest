# 新闻音频摘要系统设计文档

## 项目概述

每天早上 8:00 自动抓取多元化新闻，生成 15 分钟中文音频摘要，推送到微信。

## 目标用户需求

- **新闻类型**：科技/互联网、财经/商业、国际/政治、流行趋势、社会热点
- **避免信息茧房**：多源、多视角
- **接收方式**：微信推送
- **时间**：早上 8:00（通勤前）
- **预算**：免费

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     GitHub Actions (定时触发)                      │
│                        每天早上 8:00 CST                          │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Python 主脚本执行                            │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ 1. 新闻抓取层 (RSS + API)                                  │  │
│  │    - RSS 解析 (feedparser)                                 │  │
│  │    - 热点抓取 (微博热搜/知乎热榜 API)                        │  │
│  │    - 内容去重、排序                                         │  │
│  └───────────────────────────────────────────────────────────┘  │
│                          │                                       │
│                          ▼                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ 2. AI 摘要生成层                                           │  │
│  │    - Kimi API / Gemini Flash (免费)                        │  │
│  │    - 生成结构化摘要 (标题 + 要点)                           │  │
│  │    - 控制输出长度 (约 2000-3000 字，15 分钟音频)             │  │
│  └───────────────────────────────────────────────────────────┘  │
│                          │                                       │
│                          ▼                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ 3. 语音合成层 (Edge TTS)                                   │  │
│  │    - 中文语音 (zh-CN-XiaoxiaoNeural)                       │  │
│  │    - 输出 MP3 文件                                         │  │
│  │    - 预估时长 15 分钟                                       │  │
│  └───────────────────────────────────────────────────────────┘  │
│                          │                                       │
│                          ▼                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ 4. 存储与推送层                                            │  │
│  │    - 上传音频到 GitHub Release / R2                        │  │
│  │    - Pushplus 推送到微信                                    │  │
│  │    - 消息格式: 标题 + 摘要文本 + 音频链接                    │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 新闻源配置

### RSS 源 (12-15 个)

| 分类 | 来源 | RSS 地址 |
|------|------|----------|
| **科技** | 36氪 | https://36kr.com/feed |
| | 虎嗅 | https://www.huxiu.com/rss/0.xml |
| | 极客公园 | https://www.geekpark.net/rss |
| **财经** | 财新网 | https://rsshub.app/caixin/finance |
| | 华尔街见闻 | https://rsshub.app/wallstreetcn/news/global |
| **国际** | BBC 中文 | https://feeds.bbci.co.uk/zhongwen/simp/rss.xml |
| | 路透社 | https://cn.reuters.com/rssFeed/worldNews |
| **热点** | 微博热搜 | https://rsshub.app/weibo/search/hot |
| | 知乎日报 | https://rsshub.app/zhihu/daily |
| **综合** | 澎湃新闻 | https://rsshub.app/thepaper/featured |
| | 界面新闻 | https://www.jiemian.com/rss/news.xml |

> 注：部分源使用 RSSHub（开源 RSS 生成工具）获取

### 热点补充 (API)

- 微博热搜前 10
- 知乎热榜前 10
- 抖音热点（可选）

---

## 核心组件设计

### 1. 配置管理 (`config.py`)

```python
# 新闻源配置
RSS_SOURCES = {
    "tech": [...],
    "finance": [...],
    "international": [...],
    "hot": [...],
}

# API 配置 (从环境变量读取)
KIMI_API_KEY = os.getenv("KIMI_API_KEY")
PUSHPLUS_TOKEN = os.getenv("PUSHPLUS_TOKEN")

# 输出配置
AUDIO_DURATION_TARGET = 15 * 60  # 15 分钟 (秒)
MAX_NEWS_PER_CATEGORY = 5
```

### 2. 新闻抓取器 (`fetcher.py`)

```python
class NewsFetcher:
    def fetch_rss(self, url: str) -> list[NewsItem]
    def fetch_weibo_hot(self) -> list[NewsItem]
    def fetch_zhihu_hot(self) -> list[NewsItem]
    def deduplicate(self, items: list[NewsItem]) -> list[NewsItem]
    def prioritize(self, items: list[NewsItem]) -> list[NewsItem]
```

### 3. AI 摘要生成 (`summarizer.py`)

```python
class Summarizer:
    def __init__(self, api_key: str)
    def generate_summary(self, news_items: list[NewsItem]) -> str
    def format_for_tts(self, summary: str) -> str
```

**Prompt 模板**：
```
你是一位新闻主播，请用口语化的方式总结今天的新闻。

要求：
1. 总时长控制在 15 分钟左右（约 2500 字）
2. 使用播报风格，有开场白和结束语
3. 分类播报：科技、财经、国际、热点
4. 每条新闻用 2-3 句话概括要点
5. 语气轻松但不失专业

今日新闻内容：
{news_content}
```

### 4. 语音合成 (`tts.py`)

```python
class TTSEngine:
    def generate_audio(self, text: str, output_path: str) -> str
    def estimate_duration(self, text: str) -> int
```

使用 `edge-tts` 库：
```python
import edge_tts

communicate = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural")
await communicate.save(output_path)
```

### 5. 推送服务 (`pusher.py`)

```python
class WeChatPusher:
    def __init__(self, token: str)
    def send(self, title: str, content: str, audio_url: str) -> bool
```

Pushplus API：
```python
requests.post("http://www.pushplus.plus/send", json={
    "token": token,
    "title": title,
    "content": f"{content}\n\n🎧 [点击收听音频]({audio_url})",
    "template": "markdown"
})
```

---

## GitHub Actions 工作流

```yaml
# .github/workflows/daily-news.yml
name: Daily News Audio Digest

on:
  schedule:
    - cron: '0 0 * * *'  # UTC 0:00 = CST 8:00
  workflow_dispatch:  # 手动触发

jobs:
  generate-digest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run news digest
        env:
          KIMI_API_KEY: ${{ secrets.KIMI_API_KEY }}
          PUSHPLUS_TOKEN: ${{ secrets.PUSHPLUS_TOKEN }}
        run: python main.py
      
      - name: Upload audio artifact
        uses: actions/upload-artifact@v4
        with:
          name: daily-audio
          path: output/*.mp3
```

---

## 文件结构

```
daily-news-digest/
├── .github/
│   └── workflows/
│       └── daily-news.yml
├── src/
│   ├── __init__.py
│   ├── config.py          # 配置管理
│   ├── fetcher.py         # 新闻抓取
│   ├── summarizer.py      # AI 摘要
│   ├── tts.py             # 语音合成
│   └── pusher.py          # 推送服务
├── output/                # 输出目录
├── main.py                # 主入口
├── requirements.txt       # 依赖
└── README.md
```

---

## 依赖库

```txt
# requirements.txt
feedparser>=6.0.0        # RSS 解析
edge-tts>=6.1.0          # 语音合成
requests>=2.28.0         # HTTP 请求
python-dotenv>=1.0.0     # 环境变量
```

---

## 免费资源清单

| 资源 | 免费额度 | 用途 |
|------|----------|------|
| Kimi API | 每月免费调用 | AI 摘要 |
| Pushplus | 每天 200 条 | 微信推送 |
| GitHub Actions | 每月 2000 分钟 | 定时任务 |
| GitHub Releases | 无限存储 | 音频文件存储 |

---

## 错误处理

1. **RSS 源失效**：跳过该源，继续抓取其他源
2. **API 调用失败**：重试 3 次，记录日志
3. **音频生成失败**：降级为纯文本推送
4. **推送失败**：记录日志，发送邮件通知

---

## 扩展性设计

### 未来可添加功能

1. **个性化订阅**：用户自定义关注的新闻类型
2. **多语言支持**：英文新闻摘要
3. **播客发布**：生成 RSS Feed，订阅到播客 App
4. **历史归档**：自动保存历史摘要
5. **Web 界面**：查看历史摘要、管理订阅

---

## 成功指标

- ✅ 每天早上 8:00 准时推送
- ✅ 音频时长 12-18 分钟
- ✅ 涵盖 4+ 新闻类别
- ✅ 微信消息可点击收听
- ✅ 完全免费运行