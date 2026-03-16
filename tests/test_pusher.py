from unittest.mock import patch, Mock
from src.pusher import WeChatPusher


class TestWeChatPusher:
    def test_init_with_token(self):
        pusher = WeChatPusher("test_token")
        assert pusher.token == "test_token"

    @patch("src.pusher.requests.post")
    def test_send_success(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"code": 200}
        mock_post.return_value = mock_response

        pusher = WeChatPusher("test_token")
        result = pusher.send(
            title="测试标题",
            content="测试内容",
            audio_url="https://example.com/audio.mp3",
        )

        assert result is True
        mock_post.assert_called_once()

    @patch("src.pusher.requests.post")
    def test_send_failure(self, mock_post):
        mock_post.side_effect = Exception("Network error")

        pusher = WeChatPusher("test_token")
        result = pusher.send(
            title="测试标题",
            content="测试内容",
            audio_url="https://example.com/audio.mp3",
        )

        assert result is False

    def test_format_message(self):
        pusher = WeChatPusher("test_token")
        message = pusher._format_message(
            title="今日新闻",
            content="新闻内容",
            audio_url="https://example.com/audio.mp3",
        )

        assert "今日新闻" in message["title"]
        assert "新闻内容" in message["content"]
        assert "https://example.com/audio.mp3" in message["content"]