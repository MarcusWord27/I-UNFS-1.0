import json
from src.analyzer import nonmutual

def test_nonmutual_and_protected(tmp_path):
    followers = tmp_path / "followers.json"
    following = tmp_path / "following.json"
    def records(names):
        return [{"string_list_data": [{"value": n}]} for n in names]
    followers.write_text(json.dumps(records(["alice"])), encoding="utf-8")
    following.write_text(json.dumps({"relationships_following": records(["alice", "Bob", "carol"])}), encoding="utf-8")
    assert nonmutual(followers, following, ["BOB"]) == ["carol"]
