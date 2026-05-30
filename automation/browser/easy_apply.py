from typing import Optional
from playwright.sync_api import Page
from automation.browser.selectors import LINKEDIN
from automation.browser.form_filler import fill_form_step
from automation.browser.uploader import upload_resume_to_page
from automation.utils.helpers import find_element_with_fallbacks
from automation.utils.logger import get_logger
from automation.config import config

logger = get_logger(__name__)

MAX_STEPS = 12  # Safety cap — LinkedIn Easy Apply rarely exceeds 5 steps


def click_easy_apply(page: Page) -> bool:
    """
    Click the Easy Apply button on the job detail panel.
    Returns True if the modal opened successfully.
    """
    try:
        btn = find_element_with_fallbacks(page, LINKEDIN['easy_apply_button'])
        if not btn:
            return False

        btn.click()
        page.wait_for_timeout(5000)

        modal = page.query_selector(LINKEDIN['modal'])
        if modal and modal.is_visible():
            logger.info("Easy Apply modal opened")
            return True

        logger.warning("Easy Apply button clicked but modal did not appear")
        return False

    except Exception as e:
        logger.error(f"Error clicking Easy Apply: {e}")
        return False


def run_easy_apply_flow(
    page: Page,
    resume_data: dict,
    ai_engine,
    resume_file_path: str,
) -> bool:
    """
    Drive the complete multi-step Easy Apply modal.

    Steps handled automatically:
      - File upload (resume)
      - Text / number / email inputs
      - Dropdown selects
      - Radio buttons
      - Checkboxes
      - Textareas (cover letter, summary)
      - Next / Review / Submit button sequencing
      - Human approval before final submit

    Returns:
        True if application was submitted, False otherwise.
    """
    logger.info("Starting Easy Apply flow")

    for step_num in range(1, MAX_STEPS + 1):
        # Wait for modal to be stable
        try:
            page.wait_for_selector(LINKEDIN['modal'], timeout=10000, state='visible')
            page.wait_for_timeout(1200)
        except Exception:
            logger.warning(f"Modal not found at step {step_num} — exiting flow")
            break

        logger.info(f"── Step {step_num} ──")

        # Handle file upload if visible
        file_input = page.query_selector('input[type="file"]')
        if file_input and _is_visible(file_input):
            logger.info("Resume upload field detected")
            upload_resume_to_page(page, resume_file_path)
            page.wait_for_timeout(2000)

        # Fill all visible form fields
        fill_form_step(page, resume_data, ai_engine)
        page.wait_for_timeout(800)

        # Determine which button to click next
        submit_btn = find_element_with_fallbacks(page, LINKEDIN['submit_button'])
        review_btn = find_element_with_fallbacks(page, LINKEDIN['review_button'])
        next_btn = find_element_with_fallbacks(page, LINKEDIN['next_button'])

        if submit_btn and _is_visible(submit_btn):
            return _handle_submit(page, submit_btn)

        elif review_btn and _is_visible(review_btn):
            logger.info("Clicking Review button")
            review_btn.click()
            page.wait_for_timeout(2000)

        elif next_btn and _is_visible(next_btn):
            logger.info("Clicking Next button")
            next_btn.click()
            page.wait_for_timeout(2000)

        else:
            logger.warning("No navigation button found — modal may be stuck")
            break

    logger.error("Easy Apply flow ended without submission")
    _dismiss_modal(page)
    return False


def _handle_submit(page: Page, submit_button) -> bool:
    """Show human approval prompt and submit if confirmed."""
    if config.HUMAN_APPROVAL_REQUIRED:
        print()
        print("=" * 60)
        print("  APPLICATION READY TO SUBMIT")
        print("  Review the form in Chrome before confirming.")
        print("=" * 60)
        answer = input("  Press ENTER to SUBMIT  |  Type 'skip' to skip: ").strip().lower()
        print()

        if answer == 'skip':
            logger.info("User chose to skip this application")
            _dismiss_modal(page)
            return False

    try:
        submit_button.click()
        page.wait_for_timeout(3000)
        logger.info("Application submitted successfully")
        return True
    except Exception as e:
        logger.error(f"Submit click failed: {e}")
        return False


def _dismiss_modal(page: Page):
    """Close the modal without submitting."""
    try:
        dismiss = find_element_with_fallbacks(page, LINKEDIN['dismiss_button'])
        if dismiss:
            dismiss.click()
            page.wait_for_timeout(1000)

        discard = find_element_with_fallbacks(page, LINKEDIN['discard_confirm'])
        if discard:
            discard.click()
            page.wait_for_timeout(1000)
    except Exception as e:
        logger.warning(f"Modal dismiss failed: {e}")


def _is_visible(element) -> bool:
    try:
        return element.is_visible()
    except Exception:
        return False