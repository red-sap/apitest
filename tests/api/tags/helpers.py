"""标签模块断言辅助。"""


def assert_tags_body(body):
    assert isinstance(body["tags"], list), f"tags 应为列表: {body}"
