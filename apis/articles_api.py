"""文章 / 评论 / 收藏接口封装（Swagger tag: articles）。"""
from utils.rest_client import RestClient


class ArticlesApi:
    def __init__(self, client: RestClient):
        self.client = client

    def list_articles(self, params=None, headers=None, **kwargs):
        """GET /articles 文章列表，支持 tag/author/favorited/limit/offset 过滤。"""
        return self.client.get("/articles", params=params, headers=headers, **kwargs)

    def create_article(self, json=None, headers=None, **kwargs):
        """POST /articles 创建文章，body: {"article": {title, description, body, tagList}}。"""
        return self.client.post("/articles", json=json, headers=headers, **kwargs)

    def feed(self, params=None, headers=None, **kwargs):
        """GET /articles/feed 关注作者的文章流。"""
        return self.client.get("/articles/feed", params=params, headers=headers, **kwargs)

    def get_article(self, slug, headers=None, **kwargs):
        """GET /articles/{slug} 获取单篇文章。"""
        return self.client.get(f"/articles/{slug}", headers=headers, **kwargs)

    def update_article(self, slug, json=None, headers=None, **kwargs):
        """PUT /articles/{slug} 更新文章。"""
        return self.client.put(f"/articles/{slug}", json=json, headers=headers, **kwargs)

    def delete_article(self, slug, headers=None, **kwargs):
        """DELETE /articles/{slug} 删除文章。"""
        return self.client.delete(f"/articles/{slug}", headers=headers, **kwargs)

    def list_comments(self, slug, headers=None, **kwargs):
        """GET /articles/{slug}/comments 评论列表。"""
        return self.client.get(f"/articles/{slug}/comments", headers=headers, **kwargs)

    def create_comment(self, slug, json=None, headers=None, **kwargs):
        """POST /articles/{slug}/comments 创建评论，body: {"comment": {body}}。"""
        return self.client.post(f"/articles/{slug}/comments", json=json, headers=headers, **kwargs)

    def delete_comment(self, slug, comment_id, headers=None, **kwargs):
        """DELETE /articles/{slug}/comments/{id} 删除评论。"""
        return self.client.delete(f"/articles/{slug}/comments/{comment_id}", headers=headers, **kwargs)

    def favorite(self, slug, headers=None, **kwargs):
        """POST /articles/{slug}/favorite 收藏文章。"""
        return self.client.post(f"/articles/{slug}/favorite", headers=headers, **kwargs)

    def unfavorite(self, slug, headers=None, **kwargs):
        """DELETE /articles/{slug}/favorite 取消收藏。"""
        return self.client.delete(f"/articles/{slug}/favorite", headers=headers, **kwargs)
