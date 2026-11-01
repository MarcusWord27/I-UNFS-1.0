"""Create a reviewable non-follower list with fail-closed profile filters.

Instagram exports do not provide reliable private/verified status. Supply a
separate reviewed CSV with columns username,is_private,is_verified. Values
must be true/false; missing or ambiguous values are excluded from eligibility.
"""
import csv
from pathlib import Path
from src.analyzer import nonmutual

def _flag(value):
    value = str(value).strip().lower()
    if value in ("true", "1", "yes"):
        return True
    if value in ("false", "0", "no"):
        return False
    return None

def load_profile_status(path):
    statuses = {}
    if not path:
        return statuses
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not {"username", "is_private", "is_verified"}.issubset(reader.fieldnames or []):
            raise ValueError("CSV requires username,is_private,is_verified columns")
        for row in reader:
            name = (row["username"] or "").strip().lower().lstrip("@")
            if not name:
                continue
            status = (_flag(row["is_private"]), _flag(row["is_verified"]))
            if name in statuses and statuses[name] != status:
                statuses[name] = (None, None)
            else:
                statuses[name] = status
    return statuses

def build_list(followers_path, following_path, protected=(), status_csv=""):
    statuses = load_profile_status(status_csv)
    candidates = nonmutual(followers_path, following_path, protected)
    eligible, excluded = [], []
    for username in candidates:
        private, verified = statuses.get(username, (None, None))
        if private is False and verified is False:
            eligible.append(username)
        else:
            reasons = []
            if private is True:
                reasons.append("private")
            elif private is None:
                reasons.append("private status unknown")
            if verified is True:
                reasons.append("verified")
            elif verified is None:
                reasons.append("verification unknown")
            excluded.append((username, ", ".join(reasons)))
    return eligible, excluded

def export_eligible(path, eligible):
    with Path(path).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["username", "profile_url"])
        for name in eligible:
            writer.writerow([name, f"https://www.instagram.com/{name}/"])
