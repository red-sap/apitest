"""用户注册 / 登录接口封装（Swagger tag: users）。"""
from utils.rest_client import RestClient


class UsersApi:
    def __init__(self, client: RestClient):
        self.client = client

    def register(self, json=None, headers=None, **kwargs):
        """POST /users 注册新用户，body: {"user": {username, email, password}}。"""
        return self.client.post("/users", json=json, headers=headers, **kwargs)

    def login(self, json=None, headers=None, **kwargs):
        """POST /users/login 登录，body: {"user": {email, password}}。"""
        return self.client.post("/users/login", json=json, headers=headers, **kwargs)
