from src.filtered_list import load_profile_status

def test_conflicting_duplicate_never_becomes_eligible(tmp_path):
    path = tmp_path / "statuses.csv"
    path.write_text("username,is_private,is_verified\na,false,false\na,true,false\na,false,false\n")
    assert load_profile_status(path)["a"] == (None, None)
