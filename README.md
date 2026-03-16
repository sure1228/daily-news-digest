# 每日新闻音频摘要

每天早上 8:00 自动抓取多元化新闻，生成 15 分钟中文音频摘要，推送到微信。

## 功能特点

- 全自动：GitHub Actions 定时执行，无需本地运行
- 音频播报：15 分钟中文语音，通勤路上听新闻
- 微信推送：通过 Pushplus 推送到微信，无需安装 App
- 多元新闻源：科技、财经、国际、热点，避免信息茧房
- 完全免费：所有服务使用免费额度

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
pip install -r requirements.txt

export KIMI_API_KEY="your_key"
export PUSHPLUS_TOKEN="your_token"

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