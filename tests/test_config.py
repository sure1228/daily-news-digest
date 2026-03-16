from src.config import RSS_SOURCES, MAX_NEWS_PER_CATEGORY, AUDIO_DURATION_TARGET


def test_rss_sources_not_empty():
    assert len(RSS_SOURCES) > 0


def test_each_category_has_sources():
    for category, sources in RSS_SOURCES.items():
        assert len(sources) > 0, f"Category {category} has no sources"


def test_max_news_default():
    assert MAX_NEWS_PER_CATEGORY == 5


def test_audio_duration_default():
    assert AUDIO_DURATION_TARGET == 15 * 60