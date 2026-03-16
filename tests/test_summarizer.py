from unittest.mock import patch, Mock
from src.summarizer import Summarizer
from src.models import NewsItem


class TestSummarizer:
    def test_format_news_for_summary(self):
        summarizer = Summarizer("test_key")
        items = [
            NewsItem(
                title="测试标题1",
                link="https://a.com",
                summary="摘要1",
                category="tech",
                source="源A",
            ),
            NewsItem(
                title="测试标题2",
                link="https://b.com",
                summary="摘要2",
                category="finance",
                source="源B",
            ),
        ]
        formatted = summarizer.format_news_for_summary(items)
        assert "测试标题1" in formatted
        assert "测试标题2" in formatted

    def test_generate_summary_without_api_key(self):
        summarizer = Summarizer("")
        items = [
            NewsItem(
                title="测试",
                link="https://a.com",
                category="tech",
                source="测试源",
            )
        ]
        result = summarizer.generate_summary(items)
        assert result

    @patch("src.summarizer.requests.post")
    def test_send_success(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "测试摘要"}}]
        }
        mock_post.return_value = mock_response

        summarizer = Summarizer("test_key")
        items = [
            NewsItem(
                title="测试",
                link="https://a.com",
                category="tech",
                source="测试源",
            )
        ]
        result = summarizer.generate_summary(items)
        assert "测试摘要" in result