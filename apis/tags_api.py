"""标签接口封装（Swagger tag: tags）。"""
from utils.rest_client import RestClient


class TagsApi:
    def __init__(self, client: RestClient):
        self.client = client

    def list_tags(self, headers=None, **kwargs):
        """GET /tags 获取标签列表。"""
        return self.client.get("/tags", headers=headers, **kwargs)
