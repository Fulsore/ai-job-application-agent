import re
import json
from typing import Optional
from automation.utils.logger import get_logger

logger = get_logger(__name__)


def find_element_with_fallbacks(page, selectors: list) -> Optional[object]:
    """Try a list of CSS selectors and return the first matching element."""
    for selector in selectors:
        try:
            el = page.query_selector(selector)
            if el:
                return el
        except Exception:
            continue
    return None


def safe_click(page, selectors: list, timeout: int = 5000) -> bool:
    """Click element using first matching selector from list."""
    el = find_element_with_fallbacks(page, selectors)
    if el:
        try:
            el.click()
            return True
        except Exception as e:
            logger.warning(f"Click failed: {e}")
    return False


def extract_email(text: str) -> str:
    match = re.search(r'[\w.+\-]+@[\w\-]+\.[a-zA-Z]{2,}', text)
    return match.group(0) if match else ''


def extract_phone(text: str) -> str:
    # Matches international and local phone formats
    match = re.search(r'[\+]?[\d][\d\s\-\(\)]{7,}\d', text)
    if match:
        return re.sub(r'[\s\-\(\)]', '', match.group(0))
    return ''


def extract_name_heuristic(text: str) -> str:
    """
    Heuristic: The candidate's name is usually the first short line
    of the resume that contains no special characters or URLs.
    """
    lines = [l.strip() for l in text.strip().split('\n') if l.strip()]
    for line in lines[:5]:
        if (
            len(line) < 45
            and '@' not in line
            and 'http' not in line
            and not line.replace(' ', '').isdigit()
        ):
            return line
    return ''


def save_json(data: dict, path: str):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json(path: str) -> dict:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}