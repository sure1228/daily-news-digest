# 项目开发经验总结

## 项目概述

**目标**：每天早上 8:00 自动抓取多元化新闻，生成 15 分钟中文音频摘要，推送到微信。

**技术栈**：Python + GitHub Actions + Kimi API + Pushplus + Edge TTS

**成本**：完全免费

---

## 开发流程回顾

### 阶段一：需求澄清（最重要）

**错误做法**：直接开始写代码

**正确做法**：先问清楚
- 具体需求是什么？
- 有什么约束条件？
- 优先级如何？

**实际耗时**：约 10 分钟对话，但避免了后续大量返工。

### 阶段二：方案设计

**选择**：Python + GitHub Actions（而非 n8n、现成产品）

**理由**：
- 完全免费
- 可定制性强
- 代码简洁，易于维护

### 阶段三：实现

采用 TDD 模式，先写测试再写代码。20 个测试全部通过。

### 阶段四：部署与调试（坑最多）

---

## 遇到的问题与解决方案

### 问题 1：Git 推送失败

**现象**：`HTTP2 framing layer error`

**原因**：网络问题 + 认证问题

**解决方案**：
1. 设置 `git config --global http.version HTTP/1.1`
2. 使用带 token 的 URL 或 SSH

**教训**：网络问题是常见的，优先考虑认证配置。

---

### 问题 2：GitHub Actions 无法创建 Release

**现象**：`403 Resource not accessible by integration`

**原因**：GitHub Token 权限不足

**解决方案**：在 workflow 中添加权限声明：
```yaml
permissions:
  contents: write
```

**教训**：GitHub Actions 权限问题，先检查 `permissions` 配置。

---

### 问题 3：微信推送内容被截断

**现象**：只收到部分内容

**原因**：代码中手动截断了 `summary[:800]`

**解决方案**：移除截断逻辑，发送完整内容

**教训**：不要假设推送服务有长度限制，先测试再决定是否截断。

---

### 问题 4：AI 生成内容太短

**现象**：只生成 1000 字左右，不够 15 分钟

**原因**：
1. 使用的模型输出限制（8k 模型）
2. Prompt 不够明确

**解决方案**：
1. 换用更大的模型（32k）
2. 加强 Prompt，明确要求字数
3. 添加后处理函数清理废话

**教训**：AI 输出长度需要通过模型选择 + Prompt + 后处理三重保障。

---

### 问题 5：定时任务不运行（关键）

**现象**：设定了 cron 但到了时间没自动运行

**原因**：仓库 Actions 权限未正确配置

**解决方案**：
1. 检查 Settings → Actions → Workflow permissions
2. 选择 **Read and write permissions**
3. 勾选 **Allow GitHub Actions to create and approve pull requests**

**教训**：
- 这是最常见的问题，应该**第一时间检查权限设置**
- 不要急着推荐新服务，先排查配置

---

### 问题 6：音频无法在微信直接播放

**现象**：需要登录 GitHub 才能下载

**原因**：音频存在 Artifacts 中，不是公开链接

**解决方案**：使用 GitHub Release 托管，生成公开 URL

**教训**：需要公开访问的资源，用 Release 而非 Artifacts。

---

## 关键经验总结

### 1. 权限问题优先排查

GitHub Actions 不工作，90% 是权限问题。检查顺序：

1. **仓库权限**：Settings → Actions → Workflow permissions
2. **Workflow 声明**：`permissions: contents: write`
3. **Token 权限**：如果用 PAT，确保有 `workflow` scope

### 2. AI 输出质量控制

- **模型选择**：根据输出长度需求选择合适模型
- **Prompt 设计**：明确、具体、禁止事项要说清楚
- **后处理**：清理 AI 的"客套话"

### 3. 免费服务的限制

| 服务 | 免费限制 | 应对策略 |
|------|----------|----------|
| GitHub Actions | 定时任务不稳定 | 配置正确权限 + 保活机制 |
| Kimi API | 有调用限制 | 错误处理 + 降级方案 |
| Pushplus | 需要实名认证 | 提前完成认证 |

### 4. 代码结构保持简洁

```
src/
├── config.py     # 所有配置集中管理
├── models.py     # 数据模型
├── fetcher.py    # 单一职责：抓取
├── summarizer.py # 单一职责：摘要
├── tts.py        # 单一职责：语音
└── pusher.py     # 单一职责：推送
```

每个模块只做一件事，易于测试和维护。

### 5. 用户反馈优先

用户提到的问题：
- 推送广告新闻 → 添加关键词过滤
- 想看原新闻链接 → 添加链接列表

**不要过度设计**，根据实际反馈迭代。

---

## 避免的弯路

### ❌ 不要做的事

1. **不要急着推荐新服务**
   - 问题：定时任务不工作
   - 错误做法：推荐注册 cron-job.org
   - 正确做法：检查权限设置

2. **不要假设用户懂技术细节**
   - 权限设置在哪里？要给出具体链接
   - Token 怎么获取？要给出步骤

3. **不要忽视基础配置**
   - 权限、Token、认证这些基础配置是最容易出问题的
   - 遇到问题先检查基础配置

4. **不要过早优化**
   - 先让它跑起来，再考虑优化
   - 用户反馈什么问题，解决什么问题

### ✅ 应该做的事

1. **需求澄清先行**
   - 明确目标、约束、优先级
   - 避免方向性错误

2. **权限配置优先检查**
   - GitHub Actions 不工作 → 先查权限
   - 这是 90% 的问题所在

3. **保持代码简洁**
   - 单一职责
   - 易于测试
   - 避免过度设计

4. **根据反馈迭代**
   - 用户说什么问题，解决什么问题
   - 不要臆测需求

---

## 可复用的代码模式

### 1. 配置集中管理

```python
# src/config.py
RSS_SOURCES = {...}
AD_KEYWORDS = [...]
AI_PROVIDER = os.getenv("AI_PROVIDER", "kimi")
```

### 2. 权限声明模板

```yaml
permissions:
  contents: write
  actions: write
```

### 3. 错误处理模式

```python
try:
    result = api_call()
except Exception as e:
    logger.error(f"Failed: {e}")
    return fallback_value  # 降级方案
```

### 4. 新闻过滤模式

```python
def is_ad_news(title: str) -> bool:
    for keyword in AD_KEYWORDS:
        if keyword in title.lower():
            return True
    return False
```

---

## 项目文件清单

```
daily-news-digest/
├── .github/workflows/
│   ├── daily-news.yml    # 主流程
│   └── keep-alive.yml    # 保活机制
├── src/
│   ├── config.py         # 配置
│   ├── models.py         # 数据模型
│   ├── fetcher.py        # 新闻抓取
│   ├── summarizer.py     # AI 摘要
│   ├── tts.py            # 语音合成
│   └── pusher.py         # 推送
├── tests/                # 测试
├── main.py               # 入口
└── requirements.txt      # 依赖
```

---

## 最后的建议

1. **先跑通再优化**：能用 > 好用 > 完美

2. **权限问题先查**：GitHub Actions 不工作，90% 是权限

3. **保持简洁**：代码越少，问题越少

4. **听取反馈**：用户比我们更清楚需求

5. **记录经验**：踩过的坑要记下来，避免重复踩