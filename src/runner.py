"""Conservative browser runner. Stops on errors and uncertain verification."""
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright

class UnfollowRunner:
    def __init__(self, report):
        self.report = report
        self.gate = threading.Event()
        self.gate.set()
        self.cancel = threading.Event()
        self.active = False

    def pause(self):
        self.gate.clear()
        self.report("Paused")
    def resume(self):
        self.gate.set()
        self.report("Resumed")
    def stop(self):
        self.cancel.set()
        self.gate.set()
        self.report("Stop requested")

    def run(self, usernames, minimum):
        if self.active:
            self.report("A session is already running")
            return
        self.active = True
        self.cancel.clear()
        self.gate.set()
        count = 0
        try:
            with sync_playwright() as p:
                context = p.chromium.launch_persistent_context(
                    user_data_dir=str(Path.home() / ".i_unfs_browser"),
                    headless=False
                )
                page = context.pages[0] if context.pages else context.new_page()
                page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
                self.report("Log in manually in the browser if needed. Then return here and press Resume.")
                self.gate.clear()
                while not self.gate.wait(0.25):
                    if self.cancel.is_set():
                        break
                for username in usernames:
                    if self.cancel.is_set():
                        break
                    self.gate.wait()
                    if self.cancel.is_set():
                        break
                    try:
                        page.goto(f"https://www.instagram.com/{username}/", wait_until="domcontentloaded", timeout=30000)
                        # Fail closed: no reliable public interface for differentiating
                        # Meta Verified and legacy verification. Only proceed if badge
                        # absence can be confirmed by a maintained, tested adapter.
                        verification = self._verification_status(page)
                        if verification is not False:
                            self.report(f"Skipped @{username}: verified or unknown")
                            continue
                        button = page.get_by_role("button", name="Following", exact=True)
                        if button.count() != 1:
                            raise RuntimeError("Following button not uniquely found")
                        button.click()
                        confirm = page.get_by_role("button", name="Unfollow", exact=True)
                        if confirm.count() != 1:
                            raise RuntimeError("Unfollow confirmation missing or ambiguous")
                        confirm.click()
                        count += 1
                        self.report(f"Unfollow attempted @{username} ({count}/{len(usernames)})")
                    except Exception as exc:
                        self.gate.clear()
                        self.report(f"Paused on @{username}: {exc}. Stop and inspect browser.")
                        # Stop instead of automatically retrying or bypassing restrictions.
                        break
                context.close()
        except Exception as exc:
            self.gate.clear()
            self.report(f"Session stopped on browser error: {exc}")
        finally:
            self.active = False
            self.report(f"Session ended. {count} unfollow actions attempted; minimum requested: {minimum}")

    @staticmethod
    def _verification_status(page):
        # Unknown until a stable, independently tested verification detector exists.
        # Deliberately fail closed instead of unfollowing potentially verified users.
        return None
