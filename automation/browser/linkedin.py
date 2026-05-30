from typing import Optional
from playwright.sync_api import Page, ElementHandle
from automation.browser.selectors import LINKEDIN
from automation.utils.helpers import find_element_with_fallbacks
from automation.utils.logger import get_logger

logger = get_logger(__name__)


def navigate_to_linkedin_jobs(page: Page, keywords: list, location: str = '') -> bool:
    """
    Navigate to LinkedIn Jobs and perform a search.

    Args:
        page: Playwright page connected to Chrome
        keywords: List of search keywords extracted from resume
        location: Job location string (e.g. "Hyderabad" or "Remote")

    Returns:
        True if navigation succeeded
    """
    try:
        logger.info(f"Navigating to LinkedIn Jobs | keywords={keywords} | location={location}")
        page.goto(
    'https://www.linkedin.com/jobs/',
    wait_until='domcontentloaded',
    timeout=60000
)
        page.wait_for_timeout(2500)
        keyword_string = "%20".join(keywords[:4])
        search_url = (
    f"https://www.linkedin.com/jobs/search/"
    f"?keywords={keyword_string}"
    f"&location={location}"
)
        logger.info(f"Opening search URL: {search_url}")
        page.goto(
    search_url,
    wait_until="domcontentloaded",
    timeout=60000
)
        page.wait_for_timeout(5000)
        page.wait_for_timeout(5000)

        # Apply Easy Apply filter
        _apply_easy_apply_filter(page)

        return True

    except Exception as e:
        logger.error(f"LinkedIn navigation failed: {e}")
        return False


def _apply_easy_apply_filter(page: Page):
    """Click the Easy Apply filter button if present."""
    try:
        btn = find_element_with_fallbacks(page, LINKEDIN['easy_apply_filter'])
        if btn:
            btn.click()
            page.wait_for_timeout(2000)
            logger.info("Easy Apply filter applied")
        else:
            logger.info("Easy Apply filter button not found — continuing without filter")
    except Exception as e:
        logger.warning(f"Could not apply Easy Apply filter: {e}")


def get_job_cards(page: Page) -> list:
    """Return all visible job card elements."""
    page.wait_for_timeout(2000)

    for selector in LINKEDIN['job_cards']:
        try:
            cards = page.query_selector_all(selector)
            if cards:
                logger.info(f"Found {len(cards)} job cards using '{selector}'")
                return cards
        except Exception:
            continue

    logger.warning("No job cards found — check if LinkedIn is open and logged in")
    return []


def open_job_from_card(page: Page, card: ElementHandle) -> Optional[dict]:
    """
    Scroll card into view, click it, wait for detail panel to load,
    then extract and return job info dict.
    """
    try:
        card.scroll_into_view_if_needed()
        page.wait_for_timeout(300)
        card.click()
        page.wait_for_timeout(2500)

        return extract_job_details(page)

    except Exception as e:
        logger.error(f"Error opening job card: {e}")
        return None


def extract_job_details(page: Page) -> dict:
    """Extract job metadata from the detail panel on the right side."""
    info = {'title': '', 'company': '', 'description': '', 'url': page.url}

    title_el = find_element_with_fallbacks(page, LINKEDIN['detail_title'])
    if title_el:
        info['title'] = title_el.inner_text().strip()

    company_el = find_element_with_fallbacks(page, LINKEDIN['detail_company'])
    if company_el:
        info['company'] = company_el.inner_text().strip()

    desc_el = find_element_with_fallbacks(page, LINKEDIN['detail_description'])
    if desc_el:
        info['description'] = desc_el.inner_text().strip()[:4000]

    return info


def scroll_job_results(page: Page, times: int = 4):
    """Scroll the left job list panel to load more results."""
    try:
        # LinkedIn's left panel selector
        panel = page.query_selector('.jobs-search-results-list, .scaffold-layout__list')
        if panel:
            for _ in range(times):
                panel.evaluate('el => el.scrollBy(0, 600)')
                page.wait_for_timeout(700)
    except Exception as e:
        logger.warning(f"Scroll failed: {e}")