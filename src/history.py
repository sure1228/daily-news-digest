import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Set


logger = logging.getLogger(__name__)

HISTORY_FILE = Path("output/news_history.json")
MAX_HISTORY_DAYS = 7


def load_history() -> Set[str]:
    if not HISTORY_FILE.exists():
        return set()
    
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data.get("titles", []))
    except Exception as e:
        logger.error(f"Failed to load history: {e}")
        return set()


def save_history(titles: Set[str]) -> None:
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "titles": list(titles),
                "updated": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {len(titles)} titles to history")
    except Exception as e:
        logger.error(f"Failed to save history: {e}")


def is_duplicate(title: str, history: Set[str]) -> bool:
    normalized = title.strip().lower()[:50]
    return normalized in history


def filter_duplicates(titles: List[str]) -> List[str]:
    history = load_history()
    
    unique_titles = []
    for title in titles:
        if not is_duplicate(title, history):
            unique_titles.append(title)
            normalized = title.strip().lower()[:50]
            history.add(normalized)
    
    logger.info(f"Filtered {len(titles) - len(unique_titles)} duplicates")
    
    history = set(list(history)[-500:])
    save_history(history)
    
    return unique_titles


def add_to_history(titles: List[str]) -> None:
    history = load_history()
    
    for title in titles:
        normalized = title.strip().lower()[:50]
        history.add(normalized)
    
    history = set(list(history)[-500:])
    save_history(history)