"""Read Instagram export JSON and identify non-mutual accounts."""
import json
from pathlib import Path

def usernames(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = next((v for v in data.values() if isinstance(v, list)), [])
    names = set()
    for item in data:
        for record in item.get("string_list_data", []):
            name = record.get("value", "").strip().lower()
            if name:
                names.add(name)
    return names

def nonmutual(followers_path, following_path, protected=()):
    followers = usernames(followers_path)
    following = usernames(following_path)
    return sorted((following - followers) - {x.strip().lower() for x in protected})
