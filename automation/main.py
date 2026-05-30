
"""
AI Job Application Agent — Multi Platform Version
Platforms:
- LinkedIn
- Wellfound
"""

import sys
import os
import argparse
import datetime

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from automation.browser.launch_browser import launch_browser

# LinkedIn
from automation.browser.linkedin import (
    navigate_to_linkedin_jobs,
    get_job_cards,
    open_job_from_card,
    scroll_job_results,
)

# Wellfound
from automation.browser.wellfound import (
    navigate_to_wellfound_jobs,
    get_wellfound_job_count,
    open_wellfound_job_from_index,
    scroll_wellfound_job_results,
)

from automation.browser.easy_apply import (
    click_easy_apply,
    run_easy_apply_flow,
)

from automation.ai.resume_parser import ResumeParser
from automation.ai.answer_generator import AnswerGenerator
from automation.ai.job_ranker import JobRanker

from automation.config import config
from automation.utils.logger import get_logger

logger = get_logger("main")


def parse_args():
    p = argparse.ArgumentParser(description="AI Job Application Agent")

    p.add_argument(
        "--resume",
        default=config.DEFAULT_RESUME_PATH,
        help="Resume PDF path",
    )

    p.add_argument(
        "--keywords",
        nargs="+",
        default=[],
        help="Search keywords",
    )

    p.add_argument(
        "--location",
        default="",
        help="Location",
    )

    p.add_argument(
        "--max-jobs",
        type=int,
        default=10,
        help="Max jobs",
    )

    p.add_argument(
        "--min-score",
        type=float,
        default=0.08,
        help="Minimum relevance score",
    )

    return p.parse_args()


def run_platform(
    page,
    platform_name,
    navigate_fn,
    get_cards_fn,
    open_card_fn,
    scroll_fn,
    keywords,
    location,
    resume_data,
    resume_path,
    ai_engine,
    ranker,
    max_jobs,
    min_score,
):
    """
    Generic platform runner
    """

    logger.info(f"========== STARTING {platform_name.upper()} ==========")

    ok = navigate_fn(page, keywords, location)

    if not ok:
        logger.error(f"{platform_name} navigation failed")
        return []

    scroll_fn(page, times=4)

    cards = get_cards_fn(page)

    if not cards:
        logger.warning(f"No cards found on {platform_name}")
        return []

    logger.info(f"{platform_name}: Found {len(cards)} cards")

    applied_jobs = []

    for idx, card in enumerate(cards):

        if len(applied_jobs) >= max_jobs:
            break

        print(f"\n[{platform_name}] {idx + 1}/{len(cards)}")

        try:
            job_info = open_card_fn(page, card)

            if not job_info:
                continue

            title = job_info.get("title", "")
            company = job_info.get("company", "")

            logger.info(f"{title} @ {company}")

            score = ranker.score_job(
                resume_data["raw_text"],
                job_info.get("description", ""),
                title,
            )

            logger.info(f"Score: {score:.4f}")

            if score < min_score:
                logger.info("Below threshold")
                continue

            modal_ok = click_easy_apply(page)

            if not modal_ok:
                logger.info("No easy apply")
                continue

            submitted = run_easy_apply_flow(
                page=page,
                resume_data=resume_data,
                ai_engine=ai_engine,
                resume_file_path=resume_path,
            )

            if submitted:

                applied_jobs.append({
                    "platform": platform_name,
                    "title": title,
                    "company": company,
                    "score": score,
                    "submitted_at": datetime.datetime.now().isoformat(),
                })

                logger.info(f"APPLIED: {title}")

            page.wait_for_timeout(2000)

        except Exception as e:
            logger.error(f"{platform_name} error: {e}")

    return applied_jobs


def main():

    args = parse_args()

    print("\n" + "=" * 64)
    print("AI JOB APPLICATION AGENT")
    print("=" * 64)

    resume_path = os.path.abspath(args.resume)

    if not os.path.isfile(resume_path):
        logger.error(f"Resume missing: {resume_path}")
        sys.exit(1)

    parser = ResumeParser()

    resume_data = parser.parse(resume_path)

    if not resume_data.get("raw_text"):
        logger.error("Resume parsing failed")
        sys.exit(1)

    resume_data["resume_path"] = resume_path

    ranker = JobRanker()
    ai_engine = AnswerGenerator()

    if args.keywords:
        keywords = args.keywords
    else:
        keywords = ranker.extract_keywords(
            resume_data["raw_text"],
            top_n=8,
        )

    print()
    print("Start Chrome with remote debugging first")
    input("Press ENTER when ready...")

    playwright, page = launch_browser()

    all_applied = []

    # =========================================================
    # LINKEDIN
    # =========================================================

    linkedin_results = run_platform(
        page=page,
        platform_name="linkedin",

        navigate_fn=navigate_to_linkedin_jobs,
        get_cards_fn=get_job_cards,
        open_card_fn=open_job_from_card,
        scroll_fn=scroll_job_results,

        keywords=keywords,
        location=args.location,

        resume_data=resume_data,
        resume_path=resume_path,

        ai_engine=ai_engine,
        ranker=ranker,

        max_jobs=args.max_jobs,
        min_score=args.min_score,
    )

    all_applied.extend(linkedin_results)

    # =========================================================
    # WELLFOUND
    # =========================================================

    wellfound_results = run_platform(
        page=page,
        platform_name="wellfound",

        navigate_fn=navigate_to_wellfound_jobs,
        get_cards_fn=get_wellfound_job_count,
        open_card_fn=open_wellfound_job_from_index,
        scroll_fn=scroll_wellfound_job_results,

        keywords=keywords,
        location=args.location,

        resume_data=resume_data,
        resume_path=resume_path,

        ai_engine=ai_engine,
        ranker=ranker,

        max_jobs=args.max_jobs,
        min_score=args.min_score,
    )

    all_applied.extend(wellfound_results)

    print("\n" + "=" * 64)
    print("SESSION COMPLETE")
    print("=" * 64)

    print(f"Total Applied: {len(all_applied)}")

    for job in all_applied:
        print(
            f"• [{job['platform']}] "
            f"{job['title']} @ {job['company']} "
            f"({job['score']:.3f})"
        )

    print("=" * 64)

    playwright.stop()


if __name__ == "__main__":
    main()