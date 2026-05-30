import os
from playwright.sync_api import Page
from automation.utils.logger import get_logger

logger = get_logger(__name__)


def upload_resume_to_page(page: Page, resume_path: str) -> bool:
    """
    Upload a resume PDF to the file input in the current modal.

    Args:
        page: Active Playwright page
        resume_path: Absolute path to the resume PDF file

    Returns:
        True if upload succeeded
    """
    if not os.path.isfile(resume_path):
        logger.error(f"Resume file does not exist: {resume_path}")
        return False

    try:
        file_input = page.query_selector('input[type="file"]')
        if not file_input:
            logger.warning("No file input element found on page")
            return False

        file_input.set_input_files(resume_path)
        page.wait_for_timeout(2500)
        logger.info(f"Resume uploaded: {os.path.basename(resume_path)}")
        return True

    except Exception as e:
        logger.error(f"Resume upload failed: {e}")
        return False