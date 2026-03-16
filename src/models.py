from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional


@dataclass
class NewsItem:
    title: str
    link: str
    category: str
    source: str
    summary: str = ""
    published: Optional[datetime] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class DigestResult:
    date: str
    title: str
    summary_text: str
    audio_path: str
    audio_duration: float = 0.0
    news_count: int = 0