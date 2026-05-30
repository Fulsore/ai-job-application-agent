import sys
from playwright.sync_api import sync_playwright, Page
from automation.utils.logger import get_logger
from automation.config import config

logger = get_logger(__name__)


def launch_browser():
    """
    Connect to an already-running Chrome via Chrome DevTools Protocol (CDP).

    REQUIRES Chrome to be running with:
        chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug

    Returns:
        (playwright_instance, page) — caller must call playwright.stop() when done
    """
    playwright = sync_playwright().start()

    logger.info(f"Connecting to Chrome at {config.CHROME_CDP_URL}")

    try:
        browser = playwright.chromium.connect_over_cdp(config.CHROME_CDP_URL)
    except Exception as e:
        logger.error(
            f"\n\nCannot connect to Chrome.\n"
            f"Start Chrome first with:\n"
            f"  Windows:  chrome.exe --remote-debugging-port=9222 --user-data-dir=C:\\ChromeDebug\n"
            f"  Mac:      /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome "
            f"--remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug\n"
            f"  Linux:    google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug\n"
            f"\nOriginal error: {e}\n"
        )
        playwright.stop()
        sys.exit(1)

    contexts = browser.contexts
    if not contexts:
        logger.error("No browser context found. Open a tab in Chrome first.")
        playwright.stop()
        sys.exit(1)

    context = contexts[0]
    pages = context.pages
    page = context.new_page()

    logger.info("Browser connected successfully")
    return playwright, page