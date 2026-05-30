"""
Fills all form fields in the current Easy Apply modal step.

Priority for filling a field:
  1. Check FIELD_MAP for a regex match on the label text → use resume_data value
  2. Fall back to AI-generated answer via ai_engine.generate_answer()
"""

import re
from typing import Optional
from playwright.sync_api import Page
from automation.utils.logger import get_logger

logger = get_logger(__name__)

# Maps label regex patterns to resume_data dict keys
FIELD_MAP = {
    r'phone|mobile|contact number': 'phone',
    r'^first name$|^given name$': 'first_name',
    r'^last name$|^surname$|^family name$': 'last_name',
    r'^(full name|your name|name)$': 'full_name',
    r'years.*(experience|exp)|experience.*years': 'years_of_experience',
    r'notice period|notice': 'notice_period',
    r'expected salary|salary expectation|desired salary|ctc expected': 'expected_salary',
    r'current (salary|ctc)': 'current_salary',
    r'city|current location|location': 'city',
    r'linkedin': 'linkedin_url',
    r'website|portfolio|github': 'website',
    r'email': 'email',
    r'zip|postal|pin code': 'zip_code',
    r'cover letter|summary|about yourself|tell us': 'cover_letter',
}


def fill_form_step(page: Page, resume_data: dict, ai_engine) -> None:
    """Fill all visible form field containers in the current modal step."""
    containers = _get_form_containers(page)
    logger.debug(f"Found {len(containers)} form containers")

    for container in containers:
        try:
            _process_container(page, container, resume_data, ai_engine)
        except Exception as e:
            logger.warning(f"Error filling container: {e}")


# ── Container Collectors ───────────────────────────────────────────────────────

def _get_form_containers(page: Page) -> list:
    """Collect visible form element containers from the modal."""
    selectors = [
        '.fb-form-element',
        '.jobs-easy-apply-form-section__fields .artdeco-text-input-container',
        '.jobs-easy-apply-form-element',
    ]
    for sel in selectors:
        els = page.query_selector_all(sel)
        visible = [e for e in els if _visible(e)]
        if visible:
            return visible
    return []


# ── Container Processor ────────────────────────────────────────────────────────

def _process_container(page: Page, container, resume_data: dict, ai_engine) -> None:
    """Detect the input type inside a container and fill it."""

    label = _get_label(container)

    # Skip file inputs — handled in easy_apply.py
    if container.query_selector('input[type="file"]'):
        return

    # Select dropdown
    sel = container.query_selector('select')
    if sel and _visible(sel):
        _fill_select(sel, label, resume_data, ai_engine)
        return

    # Radio group
    radios = container.query_selector_all('input[type="radio"]')
    if radios:
        _fill_radios(container, radios, label, resume_data, ai_engine)
        return

    # Checkboxes (agreement / consent)
    checkboxes = container.query_selector_all('input[type="checkbox"]')
    if checkboxes:
        _fill_checkboxes(checkboxes, label)
        return

    # Textarea
    ta = container.query_selector('textarea')
    if ta and _visible(ta):
        val = _resolve_value(label, resume_data, ai_engine, long_form=True)
        if val:
            ta.fill(val)
        return

    # Text / number / tel / email input
    inp = container.query_selector(
        'input[type="text"], input[type="number"], input[type="tel"], input[type="email"]'
    )
    if inp and _visible(inp):
        val = _resolve_value(label, resume_data, ai_engine)
        if val:
            inp.fill(str(val))
        return


# ── Field-type Handlers ────────────────────────────────────────────────────────

def _fill_select(sel_el, label: str, resume_data: dict, ai_engine) -> None:
    try:
        options = sel_el.query_selector_all('option')
        option_texts = [
            o.inner_text().strip()
            for o in options
            if o.get_attribute('value') not in (None, '', 'Select an option')
        ]
        if not option_texts:
            return

        value = _resolve_value(label, resume_data, ai_engine)
        best = _best_match(str(value), option_texts)

        if best:
            sel_el.select_option(label=best)
            logger.debug(f"SELECT '{label}' → '{best}'")
        elif option_texts:
            sel_el.select_option(label=option_texts[0])
            logger.debug(f"SELECT '{label}' → fallback '{option_texts[0]}'")
    except Exception as e:
        logger.warning(f"Select fill failed for '{label}': {e}")


def _fill_radios(container, radios, label: str, resume_data: dict, ai_engine) -> None:
    try:
        pairs = []
        for radio in radios:
            rid = radio.get_attribute('id') or ''
            lbl_el = container.query_selector(f'label[for="{rid}"]') if rid else None
            text = lbl_el.inner_text().strip() if lbl_el else ''
            pairs.append((radio, text))

        option_texts = [t for _, t in pairs if t]
        value = _resolve_value(label, resume_data, ai_engine)
        best = _best_match(str(value), option_texts)

        for radio, text in pairs:
            if text == best:
                radio.check()
                logger.debug(f"RADIO '{label}' → '{text}'")
                return

        # Fallback: check first option
        if pairs:
            pairs[0][0].check()
            logger.debug(f"RADIO '{label}' → fallback first option")
    except Exception as e:
        logger.warning(f"Radio fill failed for '{label}': {e}")


def _fill_checkboxes(checkboxes, label: str) -> None:
    """Auto-check agreement/certification checkboxes."""
    label_lower = label.lower()
    if any(w in label_lower for w in ['agree', 'certif', 'confirm', 'acknowledge', 'consent']):
        for cb in checkboxes:
            if not cb.is_checked():
                cb.check()
                logger.debug(f"CHECKBOX '{label}' → checked")


# ── Value Resolution ───────────────────────────────────────────────────────────

def _resolve_value(
    label: str,
    resume_data: dict,
    ai_engine,
    long_form: bool = False,
) -> str:
    """
    Try to resolve a form field value:
    1. Quick rule lookup in FIELD_MAP
    2. AI generation as fallback
    """
    label_lower = label.lower().strip()

    for pattern, key in FIELD_MAP.items():
        if re.search(pattern, label_lower, re.IGNORECASE):
            val = resume_data.get(key, '')
            if val:
                logger.debug(f"FIELD_MAP match '{label}' → key={key} val={val}")
                return str(val)

    # AI fallback
    if ai_engine and label_lower:
        logger.info(f"AI answering: '{label}'")
        return ai_engine.generate_answer(label, resume_data)

    return ''


def _best_match(value: str, options: list) -> Optional[str]:
    """Return the best matching option from a list (case-insensitive)."""
    if not value or not options:
        return None

    v = value.lower()

    # Exact
    for opt in options:
        if opt.lower() == v:
            return opt

    # Substring
    for opt in options:
        if v in opt.lower() or opt.lower() in v:
            return opt

    # Numeric match (for years of experience ranges like "3-5 years")
    try:
        num = int(value)
        for opt in options:
            nums = re.findall(r'\d+', opt)
            if nums and int(nums[-1]) >= num:
                return opt
    except ValueError:
        pass

    return None


# ── Helpers ────────────────────────────────────────────────────────────────────

def _get_label(container) -> str:
    try:
        el = container.query_selector('label, legend')
        if el:
            return el.inner_text().strip()

        inp = container.query_selector('input, textarea, select')
        if inp:
            return (
                inp.get_attribute('aria-label') or
                inp.get_attribute('placeholder') or ''
            )
    except Exception:
        pass
    return ''


def _visible(element) -> bool:
    try:
        return element.is_visible()
    except Exception:
        return False