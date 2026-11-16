"""当前用户模块断言辅助。"""


def assert_current_user(body, test_user):
    assert body["username"] == test_user["username"], f"username 不一致: {body}"
    assert body["email"] == test_user["email"], f"email 不一致: {body}"
