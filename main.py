import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from src.config import RSS_SOURCES, AI_API_KEY, AI_PROVIDER, PUSHPLUS_TOKEN
from src.fetcher import NewsFetcher
from src.summarizer import Summarizer
from src.tts import TTSEngine
from src.pusher import WeChatPusher
from src.models import DigestResult


load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("Starting daily news digest...")

    logger.info("Fetching news...")
    fetcher = NewsFetcher()
    news_items = fetcher.fetch_all(RSS_SOURCES)
    logger.info(f"Fetched {len(news_items)} news items")

    if not news_items:
        logger.warning("No news items fetched, exiting")
        return

    logger.info("Generating summary...")
    api_key = os.getenv("AI_API_KEY") or os.getenv("KIMI_API_KEY", AI_API_KEY)
    provider = os.getenv("AI_PROVIDER", AI_PROVIDER)
    summarizer = Summarizer(api_key, provider)
    logger.info(f"Using AI provider: {summarizer.provider}")
    summary = summarizer.generate_summary(news_items)
    logger.info(f"Summary generated: {len(summary)} characters")

    logger.info("Generating audio...")
    tts = TTSEngine()

    today = datetime.now().strftime("%Y-%m-%d")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    audio_path = str(output_dir / f"news-{today}.mp3")

    try:
        audio_path = await tts.generate_audio(summary, audio_path)
        logger.info(f"Audio generated: {audio_path}")
    except Exception as e:
        logger.error(f"Failed to generate audio: {e}")
        audio_path = None

    logger.info("Pushing to WeChat...")
    pusher = WeChatPusher(os.getenv("PUSHPLUS_TOKEN", PUSHPLUS_TOKEN))

    title = f"📰 今日新闻摘要 - {today}"
    
    audio_url = None
    if audio_path:
        repo = os.environ.get("GITHUB_REPOSITORY", "sure1228/daily-news-digest")
        audio_url = f"https://github.com/{repo}/releases/download/{today}/news-{today}.mp3"
    
    full_content = summary
    
    if audio_path:
        full_content += f"\n\n---\n\n🎧 **[点击收听音频]({audio_url})**"
    
    links_section = "\n\n---\n\n📎 **今日新闻来源**\n\n"
    seen_links = set()
    for item in news_items[:15]:
        if item.link and item.link not in seen_links:
            links_section += f"- [{item.title[:40]}...]({item.link})\n"
            seen_links.add(item.link)
    
    full_content += links_section
    
    success = pusher.send(
        title=title,
        content=full_content,
        audio_url=audio_url,
    )

    if success:
        logger.info("Push successful")
    else:
        logger.warning("Push failed")

    result = DigestResult(
        date=today,
        title=title,
        summary_text=summary,
        audio_path=audio_path or "",
        news_count=len(news_items),
    )

    text_path = output_dir / f"summary-{today}.txt"
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(summary)
    logger.info(f"Summary saved to {text_path}")

    logger.info("Daily news digest completed!")
    return result


if __name__ == "__main__":
    asyncio.run(main())