import logging
from typing import List, Dict
from datetime import datetime
import feedparser

from src.models import NewsItem
from src.config import MAX_NEWS_PER_CATEGORY


logger = logging.getLogger(__name__)


class NewsFetcher:
    def fetch_rss(self, url: str, category: str = "general") -> List[NewsItem]:
        items = []
        try:
            feed = feedparser.parse(url)
            source_name = feed.feed.get("title", url)

            for entry in feed.entries[:10]:
                item = NewsItem(
                    title=entry.get("title", "无标题"),
                    link=entry.get("link", ""),
                    summary=entry.get("summary", ""),
                    category=category,
                    source=source_name,
                    published=self._parse_published(entry),
                )
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