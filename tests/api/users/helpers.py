"""用户注册 / 登录模块断言辅助。"""


def assert_register_user(body, payload):
    """注册成功响应 user 字段断言。"""
    user = body["user"]
    sent = payload["user"]
    assert user["username"] == sent["username"], f"username 不一致: {user} vs {sent}"
    assert user["email"] == sent["email"], f"email 不一致: {user} vs {sent}"
    assert "bio" in user, "注册响应缺少 bio 字段"
    assert "image" in user, "注册响应缺少 image 字段"
    assert "password" not in user, "password 为 write_only，不应出现在响应中"
