# 每日新闻音频摘要

每天早上 8:00 自动抓取多元化新闻，生成 15 分钟中文音频摘要，推送到微信。

## 功能特点

- **全自动**：GitHub Actions 定时执行，无需本地运行
- **音频播报**：15 分钟中文语音，通勤路上听新闻
- **微信推送**：通过 Pushplus 推送到微信，无需安装 App
- **多元新闻源**：科技、财经、国际、热点、社交媒体，避免信息茧房
- **智能拆解**：自动拆解新闻集锦（如"8点1氪"），获取独立新闻
- **完全免费**：所有服务使用免费额度

---

## 部署指南

### 步骤 1：Fork 仓库

1. 打开本项目页面
2. 点击右上角 **Fork** 按钮
3. 选择自己的 GitHub 账号，点击 **Create fork**

---

### 步骤 2：获取 API Keys

#### Kimi API（AI 摘要生成）

1. 打开 https://platform.moonshot.cn/
2. 注册/登录账号
3. 进入「API Keys」页面
4. 点击「创建新的 API Key」
5. 复制保存（只显示一次）

#### Pushplus（微信推送）

1. 打开 https://www.pushplus.plus/
2. 微信扫码登录
3. **完成实名认证**（必须，否则无法发送消息）
4. 复制 Token

---

### 步骤 3：配置 Secrets

1. 打开自己 Fork 的仓库
2. 进入 **Settings → Secrets and variables → Actions**
3. 点击 **New repository secret**，添加两个：

| Name | Value |
|------|-------|
| `KIMI_API_KEY` | 你的 Kimi API Key |
| `PUSHPLUS_TOKEN` | 你的 Pushplus Token |

---

### 步骤 4：配置权限（关键！）

⚠️ **这是最容易遗漏的步骤，不配置会导致定时任务不运行**

1. 进入 **Settings → Actions → General**
2. 滚动到 **Workflow permissions** 部分
3. 选择 **Read and write permissions**
4. 勾选 **Allow GitHub Actions to create and approve pull requests**
5. 点击 **Save**

---

### 步骤 5：关注公众号

微信搜索 **「Pushplus推送加」** 并关注，新闻消息会通过这个公众号推送。

---

### 步骤 6：测试运行

1. 进入 **Actions** 标签页
2. 点击 **I understand my workflows, go ahead and enable them**
3. 左侧选择 **Daily News Audio Digest**
4. 点击右侧 **Run workflow** → **Run workflow**
5. 等待执行完成（约 2-3 分钟）
6. 检查微信是否收到推送

---

## 新闻来源

| 分类 | 来源 |
|------|------|
| 科技 | 36氪、虎嗅、IT之家、少数派 |
| 财经 | 财新网、华尔街见闻、东方财富 |
| 国际 | BBC 中文、纽约时报、德国之声 |
| 热点 | 微博热搜、知乎热榜、抖音热点 |
| 综合 | 澎湃新闻、财联社电报 |
| 社交 | 今日头条热点、小红书热门 |
| 技术社区 | GitHub Trending |

---

## 自定义

### 修改新闻源

编辑 `src/config.py` 中的 `RSS_SOURCES`：

```python
RSS_SOURCES = {
    "tech": [
        "https://36kr.com/feed",
        "https://your-rss-feed.com/feed",
    ],
}
```

### 修改推送时间

编辑 `.github/workflows/daily-news.yml`：

```yaml
schedule:
  - cron: '30 23 * * *'  # UTC 23:30 = 北京时间 7:30
```

计算方式：北京时间 = UTC 时间 + 8 小时

### 修改语音

编辑 `src/config.py`：

```python
AUDIO_VOICE = "zh-CN-YunxiNeural"  # 男声
```

可选语音：
- `zh-CN-XiaoxiaoNeural`：女声（默认）
- `zh-CN-YunxiNeural`：男声
- `zh-CN-YunjianNeural`：新闻男声

### 切换 AI 模型

在 GitHub Secrets 中添加：

| Name | Value |
|------|-------|
| `AI_PROVIDER` | `qwen` 或 `deepseek` |
| `AI_API_KEY` | 对应的 API Key |

---

## 常见问题

### 定时任务不运行？

1. **检查权限设置**（最常见）
   - Settings → Actions → General → Workflow permissions
   - 必须选择 **Read and write permissions**

2. **手动触发一次**
   - 新仓库需要手动触发来激活定时任务

3. **GitHub 定时任务延迟**
   - GitHub 官方承认定时任务可能有 5-60 分钟延迟

### 微信收不到推送？

1. 检查 Pushplus 是否完成实名认证
2. 确认已关注「Pushplus推送加」公众号
3. 检查 Secrets 中的 `PUSHPLUS_TOKEN` 是否正确

### 音频无法播放？

音频文件存储在 GitHub Release 中：
1. 进入仓库的 **Releases** 页面
2. 下载最新的 MP3 文件

---

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

---

## 项目结构

```
daily-news-digest/
├── .github/workflows/     # GitHub Actions 工作流
├── src/
│   ├── config.py          # 配置
│   ├── models.py          # 数据模型
│   ├── fetcher.py         # 新闻抓取
│   ├── collection_expander.py  # 新闻集锦拆解
│   ├── summarizer.py      # AI 摘要
│   ├── tts.py             # 语音合成
│   └── pusher.py          # 推送服务
├── tests/                 # 测试
├── main.py                # 主程序
└── requirements.txt       # 依赖
```

---

## 技术栈

| 组件 | 技术 | 成本 |
|------|------|------|
| 定时任务 | GitHub Actions | 免费（2000分钟/月） |
| AI 摘要 | Kimi API | 免费 |
| 语音合成 | Edge TTS | 免费 |
| 微信推送 | Pushplus | 免费（200条/天） |

---

## License

MIT