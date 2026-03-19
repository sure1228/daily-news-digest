import logging
import re
from typing import List, Optional
from duckduckgo_search import DDGS

from src.models import NewsItem


logger = logging.getLogger(__name__)

COLLECTION_KEYWORDS = [
    "早报", "晚报", "晨报", "日报",
    "8点1氪", "氪星晚报", "氪星早报",
    "集锦", "简报", "快讯", "速递",
]


def is_collection_news(title: str) -> bool:
    for keyword in COLLECTION_KEYWORDS:
        if keyword in title:
            return True
    return False


def extract_news_points(content: str, title: str, api_key: str = None) -> List[dict]:
    """
    从新闻集锦中提取独立的新闻点
    
    返回格式: [{"title": "新闻标题", "summary": "新闻摘要"}, ...]
    """
    if not content:
        return []
    
    news_points = []
    
    patterns = [
        r'\d+[\.、]\s*(.+?)(?=\n\d+[\.、]|\n\n|$)',
        r'【(.+?)】(.+?)(?=【|$)',
        r'●\s*(.+?)(?=●|$)',
        r'•\s*(.+?)(?=•|$)',
        r'■\s*(.+?)(?=■|$)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content, re.DOTALL)
        if matches:
            for match in matches:
                if isinstance(match, tuple):
                    text = ' '.join(match).strip()
                else:
                    text = match.strip()
                
                if len(text) > 20:
                    first_sentence = text.split('。')[0].split('，')[0][:80]
                    news_points.append({
                        "title": first_sentence,
                        "summary": text[:300],
                        "source_content": content[:500]
                    })
            break
    
    if not news_points:
        sentences = re.split(r'[。！？\n]+', content)
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 15 and not sentence.startswith('来源') and not sentence.startswith('编辑'):
                news_points.append({
                    "title": sentence[:60],
                    "summary": sentence,
                    "source_content": content[:500]
                })
    
    return news_points[:10]


def search_related_news(keyword: str, max_results: int = 3) -> List[dict]:
    """
    使用 DuckDuckGo 搜索相关新闻
    """
    try:
        results = []
        with DDGS() as ddgs:
            search_results = list(ddgs.text(keyword, max_results=max_results))
            
            for r in search_results:
                results.append({
                    "title": r.get("title", ""),
                    "link": r.get("href", ""),
                    "summary": r.get("body", ""),
                })
        
        logger.info(f"Found {len(results)} related news for: {keyword[:30]}...")
        return results
        
    except Exception as e:
        logger.error(f"Search failed for '{keyword[:30]}...': {e}")
        return []


def expand_news_point(news_point: dict, category: str) -> Optional[NewsItem]:
    """
    将新闻点扩展为完整的新闻条目
    """
    title = news_point.get("title", "")
    summary = news_point.get("summary", "")
    
    if len(title) < 10:
        return None
    
    related = search_related_news(title, max_results=2)
    
    expanded_summary = summary
    if related:
        for r in related:
            if r.get("summary"):
                expanded_summary += f" 相关报道：{r['summary'][:100]}"
                break
    
    return NewsItem(
        title=title,
        link=related[0]["link"] if related else "",
        summary=expanded_summary,
        category=category,
        source="新闻集锦拆解",
    )


def process_collection_news(item: NewsItem) -> List[NewsItem]:
    """
    处理新闻集锦，拆解成独立新闻
    """
    if not is_collection_news(item.title):
        return [item]
    
    logger.info(f"Processing collection news: {item.title[:50]}...")
    
    content = item.summary
    if not content or len(content) < 100:
        return []
    
    news_points = extract_news_points(content, item.title)
    
    if not news_points:
        return []
    
    expanded_items = []
    for point in news_points:
        expanded = expand_news_point(point, item.category)
        if expanded:
            expanded_items.append(expanded)
    
    logger.info(f"Expanded collection into {len(expanded_items)} news items")
    return expanded_items