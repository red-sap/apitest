"""文章 / 评论 / 收藏接口测试。

关联（slug/comment_id）均由 fixture 注入，测试主文件只接收准备结果并断言，
不在此处做跨接口传值、占位符解析或 try/finally 清理。
"""
import pytest

from utils.yaml_loader import load_yaml_for_parametrize
from utils.case_utils import resolve_case_placeholders, resolve_fixture_placeholders
from utils.path import CASE_PATH
from utils.assertions import assert_common
from utils.logger import logger
from tests.api.articles.helpers import assert_article_body


@pytest.mark.articles
@pytest.mark.parametrize("case", load_yaml_for_parametrize(CASE_PATH / "api/articles/list_articles.yaml"))
def test_list_articles(case, articles_api, auth_headers, test_user):
    case = resolve_fixture_placeholders(case, username=test_user["username"])
    resp = articles_api.list_articles(params=case.get("params"), headers=auth_headers)
    logger.info("文章列表响应: %s", resp.text[:300])
    expect = case["expect"]
    assert_common(resp, expect)


@pytest.mark.articles
@pytest.mark.smoke
@pytest.mark.parametrize("case", load_yaml_for_parametrize(CASE_PATH / "api/articles/create_article.yaml"))
def test_create_article(case, articles_api, auth_headers, test_user, article_cleanup):
    case = resolve_case_placeholders(case, "create_article")
    headers = None if case.get("no_auth") else auth_headers
    resp = articles_api.create_article(json=case["json"], headers=headers)
    logger.info("创建文章响应: %s", resp.text[:300])
    expect = case["expect"]
    body = assert_common(resp, expect)
    if expect["status_code"] == 201:
        article = body["article"]
        assert_article_body(article)
        assert article["title"] == case["json"]["article"]["title"]
        assert article["author"]["username"] == test_user["username"]
        article_cleanup.append(article["slug"])


@pytest.mark.articles
@pytest.mark.parametrize("case", load_yaml_for_parametrize(CASE_PATH / "api/articles/feed.yaml"))
def test_feed(case, articles_api, auth_headers):
    resp = articles_api.feed(headers=auth_headers)
    logger.info("关注流响应: %s", resp.text[:300])
    expect = case["expect"]
    assert_common(resp, expect)  # 200 + body_has_key articleCount（实现缺陷）


@pytest.mark.articles
@pytest.mark.parametrize("case", load_yaml_for_parametrize(CASE_PATH / "api/articles/get_article.yaml"))
def test_get_article(case, articles_api, auth_headers, prepared_article):
    expect = case["expect"]
    slug = case.get("slug") or prepared_article["slug"]
    resp = articles_api.get_article(slug, headers=auth_headers)
    logger.info("获取文章响应: %s", resp.text[:300])
    body = assert_common(resp, expect)
    if expect["status_code"] == 200:
        assert body["article"]["slug"] == slug


@pytest.mark.articles
@pytest.mark.parametrize("case", load_yaml_for_parametrize(CASE_PATH / "api/articles/update_article.yaml"))
def test_update_article(case, articles_api, auth_headers, second_auth_headers, prepared_article):
    case = resolve_case_placeholders(case, "update_article")
    case = resolve_fixture_placeholders(case, title=prepared_article["title"])
    headers = second_auth_headers if case.get("second_user") else auth_headers
    resp = articles_api.update_article(prepared_article["slug"], json=case["json"], headers=headers)
    logger.info("更新文章响应: %s", resp.text[:300])
    expect = case["expect"]
    body = assert_common(resp, expect)
    if expect["status_code"] == 200:
        assert body["article"]["description"] == case["json"]["article"]["description"]
        assert body["article"]["body"] == case["json"]["article"]["body"]


@pytest.mark.articles
@pytest.mark.parametrize("case", load_yaml_for_parametrize(CASE_PATH / "api/articles/delete_article.yaml"))
def test_delete_article(case, articles_api, auth_headers, second_auth_headers, prepared_article):
    headers = second_auth_headers if case.get("second_user") else auth_headers
    resp = articles_api.delete_article(prepared_article["slug"], headers=headers)
    logger.info("删除文章响应: %s", resp.text[:300])
    expect = case["expect"]
    assert_common(resp, expect)


@pytest.mark.articles
@pytest.mark.parametrize("case", load_yaml_for_parametrize(CASE_PATH / "api/articles/comment_list.yaml"))
def test_list_comments(case, articles_api, auth_headers, prepared_article, prepared_comment):
    resp = articles_api.list_comments(prepared_article["slug"], headers=auth_headers)
    logger.info("评论列表响应: %s", resp.text[:300])
    expect = case["expect"]
    body = assert_common(resp, expect)
    ids = [c["id"] for c in body["comments"]]
    assert prepared_comment["comment_id"] in ids, "评论列表应包含已创建的评论"


@pytest.mark.articles
@pytest.mark.parametrize("case", load_yaml_for_parametrize(CASE_PATH / "api/articles/comment_create.yaml"))
def test_create_comment(case, articles_api, auth_headers, prepared_article):
    case = resolve_case_placeholders(case, "create_comment")
    headers = None if case.get("no_auth") else auth_headers
    resp = articles_api.create_comment(prepared_article["slug"], json=case["json"], headers=headers)
    logger.info("创建评论响应: %s", resp.text[:300])
    expect = case["expect"]
    body = assert_common(resp, expect)
    if expect["status_code"] == 200:
        assert body["comment"]["body"] == case["json"]["comment"]["body"]


@pytest.mark.articles
@pytest.mark.parametrize("case", load_yaml_for_parametrize(CASE_PATH / "api/articles/comment_delete.yaml"))
def test_delete_comment(case, articles_api, auth_headers, prepared_comment):
    resp = articles_api.delete_comment(
        prepared_comment["slug"], prepared_comment["comment_id"], headers=auth_headers
    )
    logger.info("删除评论响应: %s", resp.text[:300])
    expect = case["expect"]
    assert_common(resp, expect)  # 204


@pytest.mark.articles
@pytest.mark.parametrize("case", load_yaml_for_parametrize(CASE_PATH / "api/articles/favorite.yaml"))
def test_favorite(case, articles_api, auth_headers, prepared_article):
    resp = articles_api.favorite(prepared_article["slug"], headers=auth_headers)
    logger.info("收藏响应: %s", resp.text[:300])
    expect = case["expect"]
    body = assert_common(resp, expect)
    if expect["status_code"] == 200:
        assert body["article"]["favorited"] is True
        assert body["article"]["favoritesCount"] >= 1


@pytest.mark.articles
@pytest.mark.parametrize("case", load_yaml_for_parametrize(CASE_PATH / "api/articles/favorite_again.yaml"))
def test_favorite_again(case, articles_api, auth_headers, favorited_article):
    resp = articles_api.favorite(favorited_article["slug"], headers=auth_headers)
    logger.info("重复收藏响应: %s", resp.text[:300])
    expect = case["expect"]
    assert_common(resp, expect)  # 200 + has_errors（Already Favourited）


@pytest.mark.articles
@pytest.mark.parametrize("case", load_yaml_for_parametrize(CASE_PATH / "api/articles/unfavorite.yaml"))
def test_unfavorite(case, articles_api, auth_headers, favorited_article):
    resp = articles_api.unfavorite(favorited_article["slug"], headers=auth_headers)
    logger.info("取消收藏响应: %s", resp.text[:300])
    expect = case["expect"]
    body = assert_common(resp, expect)
    if expect["status_code"] == 200:
        assert body["article"]["favorited"] is False


@pytest.mark.articles
@pytest.mark.e2e
@pytest.mark.parametrize("case", load_yaml_for_parametrize(CASE_PATH / "api/articles/e2e.yaml"))
def test_article_lifecycle_e2e(case, article_scenario_executor):
    expect = case["expect"]
    results = article_scenario_executor()
    steps = [
        ("create", "create_status"),
        ("read", "read_status"),
        ("comment", "comment_status"),
        ("favorite", "favorite_status"),
        ("unfavorite", "unfavorite_status"),
        ("delete", "delete_status"),
    ]
    for step, key in steps:
        resp = results.get(step)
        assert resp is not None, f"场景步骤 {step} 未执行"
        assert resp.status_code == expect[key], (
            f"步骤 {step} 期望 {expect[key]}，实际 {resp.status_code}, body={resp.text[:200]}"
        )
    created = results["create"].json()["article"]
    assert created["slug"]
    assert results["read"].json()["article"]["slug"] == created["slug"]
