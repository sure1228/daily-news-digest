import logging
from typing import List, Dict
from datetime import datetime
import feedparser

from src.models import NewsItem
from src.config import MAX_NEWS_PER_CATEGORY
from src.collection_expander import is_collection_news, process_collection_news


logger = logging.getLogger(__name__)

AD_KEYWORDS = [
    "新品发布", "新品上市", "限时优惠", "促销", "折扣",
    "戴森", "苹果发布会", "新品预售", "开售", "首发",
    "优惠", "团购", "秒杀", "特价", "满减",
    "广告", "推广", "赞助",
]

def is_ad_news(title: str) -> bool:
    title_lower = title.lower()
    for keyword in AD_KEYWORDS:
        if keyword in title_lower:
            return True
    return False


class NewsFetcher:
    def fetch_rss(self, url: str, category: str = "general") -> List[NewsItem]:
        items = []
        try:
            feed = feedparser.parse(url)
            source_name = feed.feed.get("title", url)

            for entry in feed.entries[:15]:
                title = entry.get("title", "无标题")
                
                if is_ad_news(title):
                    logger.debug(f"Filtered ad news: {title[:50]}...")
                    continue
                
                item = NewsItem(
                    title=title,
                    link=entry.get("link", ""),
                    summary=entry.get("summary", ""),
                    category=category,
                    source=source_name,
                    published=self._parse_published(entry),
                )
                
                if is_collection_news(title):
                    expanded = process_collection_news(item)
                    items.extend(expanded)
                else:
                    items.append(item)
                    
        except Exception as e:
            logger.error(f"Failed to fetch RSS {url}: {e}")

        return items

    def _parse_published(self, entry) -> datetime:
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            return datetime(*entry.published_parsed[:6])
        return datetime.now()

    def fetch_all(
        self, sources: Dict[str, List[str]], max_per_category: int = MAX_NEWS_PER_CATEGORY
    ) -> List[NewsItem]:
        all_items = []

        for category, urls in sources.items():
            category_items = []
            for url in urls:
                items = self.fetch_rss(url, category)
                category_items.extend(items)

            all_items.extend(category_items[:max_per_category])

        return self.deduplicate(all_items)

    def deduplicate(self, items: List[NewsItem]) -> List[NewsItem]:
        seen_titles = set()
        unique_items = []

        for item in items:
            normalized_title = item.title.strip().lower()
            if normalized_title not in seen_titles:
                seen_titles.add(normalized_title)
                unique_items.append(item)

        return unique_items