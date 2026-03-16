from src.fetcher import NewsFetcher
from src.models import NewsItem


class TestNewsFetcher:
    def test_fetch_rss_returns_list(self):
        fetcher = NewsFetcher()
        items = fetcher.fetch_rss("https://feeds.bbci.co.uk/zhongwen/simp/rss.xml")
        assert isinstance(items, list)

    def test_fetch_rss_items_have_required_fields(self):
        fetcher = NewsFetcher()
        items = fetcher.fetch_rss("https://feeds.bbci.co.uk/zhongwen/simp/rss.xml")
        if items:
            item = items[0]
            assert item.title
            assert item.link
            assert item.category

    def test_deduplicate_removes_duplicates(self):
        fetcher = NewsFetcher()
        items = [
            NewsItem(title="相同标题", link="https://a.com", category="tech", source="A"),
            NewsItem(title="相同标题", link="https://b.com", category="tech", source="B"),
            NewsItem(title="不同标题", link="https://c.com", category="tech", source="C"),
        ]
        deduped = fetcher.deduplicate(items)
        assert len(deduped) == 2

    def test_fetch_all_categories(self):
        fetcher = NewsFetcher()
        sources = {"tech": ["https://36kr.com/feed"]}
        items = fetcher.fetch_all(sources, max_per_category=2)
        assert isinstance(items, list)