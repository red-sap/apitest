"""文章 / 评论 / 收藏模块断言辅助。"""


def assert_article_body(article):
    assert article.get("slug"), "article 缺少 slug"
    assert article.get("title"), "article 缺少 title"
    assert isinstance(article.get("author"), dict), "article.author 应为对象"
    assert article["author"].get("username"), "article.author 缺少 username"
