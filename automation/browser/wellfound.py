from typing import Optional
from playwright.sync_api import Page
from automation.browser.selectors import WELLFOUND
from automation.utils.helpers import find_element_with_fallbacks
from automation.utils.logger import get_logger

logger = get_logger(__name__)


def navigate_to_wellfound_jobs(
    page: Page,
    keywords: list,
    location: str = "",
) -> bool:
    """
    Navigate to Wellfound jobs page
    """

    try:
        logger.info(
            f"Navigating to Wellfound | keywords={keywords} | location={location}"
        )

        keyword_string = "%20".join(keywords[:4])

        search_url = (
            f"https://wellfound.com/jobs?"
            f"q={keyword_string}"
        )

        logger.info(f"Opening URL: {search_url}")

        page.goto(
            search_url,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        page.wait_for_timeout(5000)

        return True

    except Exception as e:
        logger.error(f"Wellfound navigation failed: {e}")
        return False


def get_wellfound_job_count(page: Page) -> int:
    """
    Return number of visible job cards
    """

    try:
        for selector in WELLFOUND["job_cards"]:

            cards = page.query_selector_all(selector)

            if cards:
                logger.info(
                    f"Found {len(cards)} Wellfound cards using '{selector}'"
                )
                return len(cards)

    except Exception as e:
        logger.error(f"Failed getting Wellfound cards: {e}")

    return 0


def open_wellfound_job_from_index(
    page: Page,
    index: int,
) -> Optional[dict]:

    try:

        cards = []

        for selector in WELLFOUND["job_cards"]:

            cards = page.query_selector_all(selector)

            if cards:
                logger.info(
                    f"Using selector: {selector}"
                )
                break

        if not cards:
            logger.warning("No cards found")
            return None

        if index >= len(cards):
            return None

        card = cards[index]

        page.evaluate(
            "(el) => el.scrollIntoView({block: 'center'})",
            card,
        )

        page.wait_for_timeout(1000)

        try:
            card.click(timeout=5000)
        except:
            page.evaluate("(el) => el.click()", card)

        page.wait_for_timeout(4000)

        return extract_wellfound_job_details(page)

    except Exception as e:
        logger.error(
            f"Error opening Wellfound job card: {e}"
        )
        return None


def extract_wellfound_job_details(page: Page) -> dict:

    info = {
        "title": "",
        "company": "",
        "description": "",
        "url": page.url,
    }

    try:

        title_el = find_element_with_fallbacks(
            page,
            WELLFOUND["detail_title"],
        )

        if title_el:
            info["title"] = title_el.inner_text().strip()

        company_el = find_element_with_fallbacks(
            page,
            WELLFOUND["detail_company"],
        )

        if company_el:
            info["company"] = company_el.inner_text().strip()

        desc_el = find_element_with_fallbacks(
            page,
            WELLFOUND["detail_description"],
        )

        if desc_el:
            info["description"] = (
                desc_el.inner_text().strip()[:4000]
            )

        logger.info(
            f"Extracted job: "
            f"{info['title']} @ {info['company']}"
        )

    except Exception as e:
        logger.error(f"Extraction failed: {e}")

    return info


def scroll_wellfound_job_results(
    page: Page,
    times: int = 5,
):
    """
    Scroll page slowly to load jobs
    """

    try:

        for _ in range(times):

            page.mouse.wheel(0, 2000)

            page.wait_for_timeout(1500)

    except Exception as e:
        logger.warning(f"Scroll failed: {e}")