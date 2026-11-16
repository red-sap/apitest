"""文章 / 评论 / 收藏模块 conftest：资源准备、关联注入与场景执行器。

关联链（均在 fixture 层承载，测试主文件只接收准备好的资源并断言）：
  创建文章(prepared_article) -> 读取/更新/删除/评论/收藏
  评论(prepared_comment) 依赖 prepared_article 提供 slug
  收藏(favorited_article) 依赖 prepared_article 提供 slug
  端到端(article_scenario_executor) 显式编排创建->读取->评论->收藏->取消收藏->删除
"""
import secrets
import time

import pytest

from apis.articles_api import ArticlesApi
from utils.logger import logger


def _unique(prefix):
    return f"{prefix}_{int(time.time() * 1000)}_{secrets.token_hex(3)}"


@pytest.fixture
def articles_api(api_client):
    return ArticlesApi(api_client)


@pytest.fixture
def article_cleanup(articles_api, auth_headers):
    """记录本次创建的文章 slug，测试后逆序删除（级联清理评论与收藏）。"""
    created = []
    yield created
    for slug in reversed(created):
        try:
            r = articles_api.delete_article(slug, headers=auth_headers)
            if r.status_code not in (200, 404):
                logger.warning("[cleanup] 删除文章 %s -> %s", slug, r.status_code)
        except Exception as e:  # noqa: BLE001
            logger.warning("[cleanup] 删除文章 %s 失败: %s", slug, e)


@pytest.fixture
def prepared_article(articles_api, auth_headers, article_cleanup):
    """准备一篇本次专用文章，yield {slug, title, create_resp}。"""
    title = _unique("article")
    payload = {
        "article": {
            "title": title,
            "description": "fixture 准备的文章描述",
            "body": "fixture 准备的文章正文",
            "tagList": ["apitest"],
        }
    }
    r = articles_api.create_article(json=payload, headers=auth_headers)
    assert r.status_code == 201, f"准备文章失败: {r.status_code} {r.text[:200]}"
    slug = r.json()["article"]["slug"]
    article_cleanup.append(slug)
    logger.info("[fixture] 已准备文章 slug=%s", slug)
    return {"slug": slug, "title": title, "create_resp": r.json()}


@pytest.fixture
def prepared_comment(articles_api, prepared_article, auth_headers):
    """前置：在 prepared_article 上创建一条评论，返回 {slug, comment_id, create_resp}。"""
    r = articles_api.create_comment(
        prepared_article["slug"], json={"comment": {"body": "fixture 评论"}}, headers=auth_headers
    )
    assert r.status_code == 200, f"准备评论失败: {r.status_code} {r.text[:200]}"
    return {
        "slug": prepared_article["slug"],
        "comment_id": r.json()["comment"]["id"],
        "create_resp": r.json(),
    }


@pytest.fixture
def favorited_article(articles_api, prepared_article, auth_headers):
    """前置：收藏 prepared_article，返回 prepared_article。"""
    r = articles_api.favorite(prepared_article["slug"], headers=auth_headers)
    assert r.status_code == 200, f"准备收藏失败: {r.status_code} {r.text[:200]}"
    return prepared_article


@pytest.fixture
def article_scenario_executor(articles_api, auth_headers, article_cleanup):
    """端到端场景执行器：编排创建->读取->评论->收藏->取消收藏->删除，返回各步骤响应。"""
    def run():
        results = {}
        title = _unique("e2e_article")
        payload = {
            "article": {
                "title": title,
                "description": "e2e 描述",
                "body": "e2e 正文",
                "tagList": ["e2e"],
            }
        }
        r = articles_api.create_article(json=payload, headers=auth_headers)
        results["create"] = r
        if r.status_code != 201:
            return results
        slug = r.json()["article"]["slug"]
        article_cleanup.append(slug)
        results["read"] = articles_api.get_article(slug, headers=auth_headers)
        results["comment"] = articles_api.create_comment(
            slug, json={"comment": {"body": "e2e 评论"}}, headers=auth_headers
        )
        results["favorite"] = articles_api.favorite(slug, headers=auth_headers)
        results["unfavorite"] = articles_api.unfavorite(slug, headers=auth_headers)
        results["delete"] = articles_api.delete_article(slug, headers=auth_headers)
        return results

    return run
