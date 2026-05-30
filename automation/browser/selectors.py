"""
All CSS selectors for LinkedIn (and other platforms) in one file.
When LinkedIn changes their DOM, only update this file.
"""

LINKEDIN = {
    # ── Search ─────────────────────────────────────────────────────
    'keyword_search': [
        'input[aria-label="Search by title, skill, or company"]',
        '.jobs-search-box__text-input',
        'input.jobs-search-box__text-input',
    ],
    'location_search': [
        'input[aria-label="City, state, or zip code"]',
        'input[aria-label="Location"]',
        '.jobs-search-box__location-input',
    ],
    'easy_apply_filter': [
        'button[aria-label="Easy Apply filter."]',
        'button[aria-label*="Easy Apply"]',
        'li button[aria-label*="Easy Apply"]',
    ],

    # ── Job Cards ──────────────────────────────────────────────────
    'job_cards': [
        'li.jobs-search-results__list-item',
        '.scaffold-layout__list-item',
        '.job-card-container',
    ],
    'job_title_in_card': [
        'a.job-card-list__title',
        'a.job-card-list__title--link',
        '.job-card-container__link',
    ],
    'job_company_in_card': [
        '.job-card-container__primary-description',
        'span.job-card-container__primary-description',
    ],

    # ── Job Detail Panel ───────────────────────────────────────────
    'detail_title': [
        '.job-details-jobs-unified-top-card__job-title h1',
        '.jobs-unified-top-card__job-title',
        'h1.t-24',
    ],
    'detail_company': [
        '.job-details-jobs-unified-top-card__company-name a',
        '.jobs-unified-top-card__company-name',
    ],
    'detail_description': [
        '.jobs-description-content__text',
        '.jobs-box__html-content',
        '#job-details',
    ],

    # ── Easy Apply Button ──────────────────────────────────────────
    'easy_apply_button': [
        'button.jobs-apply-button[aria-label*="Easy Apply"]',
        '.jobs-s-apply button.jobs-apply-button',
        'button[aria-label*="Easy Apply"]',
    ],

    # ── Modal ──────────────────────────────────────────────────────
    'modal': '.jobs-easy-apply-modal',
    'next_button': [
        'button[aria-label="Continue to next step"]',
        'footer button.artdeco-button--primary',
    ],
    'review_button': [
        'button[aria-label="Review your application"]',
        'button[aria-label*="Review"]',
    ],
    'submit_button': [
        'button[aria-label="Submit application"]',
        'button[aria-label*="Submit"]',
    ],
    'dismiss_button': [
        'button[aria-label="Dismiss"]',
        'button[data-easy-apply-dismiss-button]',
    ],
    'discard_confirm': [
        'button[data-control-name="discard_application_confirm_btn"]',
        'button[aria-label="Discard"]',
        'button[aria-label="Discard application"]',
    ],

    # ── Form elements inside modal ─────────────────────────────────
    'form_element_containers': [
        '.fb-form-element',
        '.jobs-easy-apply-form-element',
        '.artdeco-text-input-container',
    ],
}

INDEED = {
    'job_cards': ['.job_seen_beacon', '.resultContent'],
    'apply_button': ['button#indeedApplyButton', 'a[data-jk]'],
}

NAUKRI = {
    'job_cards': ['.jobTuple', '.srp-jobtuple-wrapper'],
    'apply_button': ['button.btn-primary', 'a.apply-button'],
}
WELLFOUND = {

    # REAL JOB CARDS
    "job_cards": [

        'div[data-test="StartupResult"]',

        'div[class*="styles_component"]',

        'div[data-test="JobListing"]',

        'a[data-test="job-link"]',

    ],

    # TITLE
    "detail_title": [

        'h1[data-test="job-title"]',

        'h1',

        '.styles_title__',

        '[class*="title"]',

    ],

    # COMPANY
    "detail_company": [

        'a[data-test="startup-name"]',

        '[data-test="company-name"]',

        '[class*="company"]',

    ],

    # DESCRIPTION
    "detail_description": [

        'div[data-test="JobDescription"]',

        '.styles_description__',

        '[class*="description"]',

        'section',

    ],

    # APPLY BUTTON
    "easy_apply": [

        'button[data-test="apply-button"]',

        'button:has-text("Apply")',

        'a:has-text("Apply")',

    ],
}

