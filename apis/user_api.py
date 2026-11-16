"""当前用户接口封装（Swagger tag: user）。"""
from utils.rest_client import RestClient


class UserApi:
    def __init__(self, client: RestClient):
        self.client = client

    def get_current_user(self, headers=None, **kwargs):
        """GET /user 获取当前登录用户信息。"""
        return self.client.get("/user", headers=headers, **kwargs)

    def update_user(self, json=None, headers=None, **kwargs):
        """PUT /user 更新当前用户，body: {"user": {email, bio, image}}。"""
        return self.client.put("/user", json=json, headers=headers, **kwargs)
