"""用户资料 / 关注模块断言辅助。"""


def assert_profile_body(body):
    assert body["username"], "profile 缺少 username"
    assert "bio" in body
    assert "image" in body
    assert "following" in body, "profile 缺少 following 字段"
