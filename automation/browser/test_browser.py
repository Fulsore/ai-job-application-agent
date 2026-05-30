from playwright.sync_api import sync_playwright

PROFILE_PATH = "./automation_profile"

with sync_playwright() as p:

    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_PATH,
        headless=False
    )

    # Reuse existing page
    if context.pages:
        page = context.pages[0]
    else:
        page = context.new_page()

    # IMPORTANT:
    # Use "domcontentloaded" instead of "networkidle"
    page.goto(
    "https://www.linkedin.com/jobs/search/?keywords=python%20developer&location=Hyderabad",
    wait_until="domcontentloaded",
    timeout=60000
)

    print("LinkedIn opened successfully.")

    # Wait so browser stays open
    input("Press ENTER to close browser...")

    context.close()