# I-UNFS-1.0

Windows desktop Instagram non-mutual account manager (prototype).

## Setup (Windows)

1. Install Python 3.12+ and Git.
2. Clone the repository and run `python -m venv .venv`.
3. Activate with `.venv\\Scripts\\activate`.
4. Run `pip install -r requirements.txt`.
5. Run `python -m playwright install chromium`.
6. Run `python main.py`.
7. Download your Instagram follower and following information in JSON format from Instagram Accounts Center. Select the relevant files, optionally enter protected usernames, and Analyze.

## Status and limitations

**This is a prototype, not a completed automatic unfollower.** The app imports JSON exports, compares usernames, and provides bounded session controls. The Playwright runner opens a local browser and requires manual login. **Automatic unfollowing is intentionally disabled in practice:** verification status is always returned as unknown until a reliable tested detector is available. This protects Meta Verified and other verified accounts by skipping them all. The program never attempts to bypass Instagram rate limits or restrictions. Browser errors halt the session. Instagram's UI can change; the application has not been tested against a live Instagram account. Minimum is a requested target, not a guarantee.

Instagram's unofficial browser automation may violate its terms and risk account restrictions. Do not commit exports, browser profiles, credentials or session data.

## Branches

- `main`: integrated development line
- `backup/main-initial`: untouched initial repository snapshot
- `baseline/unmerged-main`: unmerged standalone entry-point baseline
- `feature/follower-analysis`, `feature/desktop-ui`, `feature/browser-unfollow`, `feature/tests-and-docs`: retained feature branches

Tests: `pytest -q`. CI tests parsing logic only; no live account automation.
