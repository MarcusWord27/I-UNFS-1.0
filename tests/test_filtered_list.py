import csv
import json
from src.filtered_list import build_list, export_eligible

def test_filtered_list_excludes_private_verified_and_unknown(tmp_path):
    followers = tmp_path / "followers.json"
    following = tmp_path / "following.json"
    statuses = tmp_path / "profiles.csv"
    followers.write_text(json.dumps([{"string_list_data":[{"value":"mutual"}]}]))
    following.write_text(json.dumps({"relationships_following":[
        {"string_list_data":[{"value":name}]} for name in ("mutual","public","private","verified","unknown","protected")
    ]}))
    with statuses.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["username","is_private","is_verified"])
        writer.writerows([["public","false","false"],["private","true","false"],["verified","false","true"]])
    eligible, excluded = build_list(followers, following, ["protected"], statuses)
    assert eligible == ["public"]
    assert {name for name, _ in excluded} == {"private","verified","unknown"}
    output = tmp_path / "list.csv"
    export_eligible(output, eligible)
    assert "https://www.instagram.com/public/" in output.read_text()
