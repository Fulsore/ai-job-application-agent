from playwright.sync_api import sync_playwright

PROFILE_PATH = "./automation_profile"

SEARCH_URL = (
    "https://www.linkedin.com/jobs/search/"
    "?keywords=python%20developer"
    "&location=Hyderabad"
)

with sync_playwright() as p:

    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_PATH,
        headless=False
    )

    # ALWAYS create fresh page
    page = context.new_page()

    page.goto(
        SEARCH_URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    # Allow LinkedIn JS rendering
    page.wait_for_timeout(8000)

    job_cards = page.locator(".job-card-container")

    count = job_cards.count()

    print(f"\nFound {count} jobs\n")

    for i in range(min(count, 10)):

        try:

            card = job_cards.nth(i)

            title = card.locator(
                ".job-card-list__title"
            ).first.text_content(timeout=5000)

            company = card.locator(
                ".artdeco-entity-lockup__subtitle"
            ).first.text_content(timeout=5000)

            print(f"{i+1}. {title}")
            print(f"   Company: {company}")
            print()

        except Exception as e:

            print(f"Job {i+1} extraction failed:")
            print(e)
            print()

    input("Press ENTER to close browser...")

    context.close()