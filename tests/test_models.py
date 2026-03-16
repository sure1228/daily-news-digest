from datetime import datetime
from src.models import NewsItem


def test_news_item_creation():
    item = NewsItem(
        title="测试新闻",
        link="https://example.com",
        summary="这是摘要",
        category="tech",
        source="测试源",
    )
    assert item.title == "测试新闻"
    assert item.category == "tech"


def test_news_item_published_time():
    now = datetime.now()
    item = NewsItem(
        title="测试",
        link="https://example.com",
        category="tech",
        source="测试",
        published=now,
    )
    assert item.published == now


def test_news_item_to_dict():
    item = NewsItem(
        title="测试",
        link="https://example.com",
        summary="摘要",
        category="tech",
        source="源",
    )
    d = item.to_dict()
    assert d["title"] == "测试"
    assert d["link"] == "https://example.com"