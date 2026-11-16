"""用户资料 / 关注接口封装（Swagger tag: profiles）。"""
from utils.rest_client import RestClient


class ProfilesApi:
    def __init__(self, client: RestClient):
        self.client = client

    def list_profiles(self, headers=None, **kwargs):
        """GET /profiles 用户资料列表。"""
        return self.client.get("/profiles", headers=headers, **kwargs)

    def create_profile(self, json=None, headers=None, **kwargs):
        """POST /profiles 创建用户资料。"""
        return self.client.post("/profiles", json=json, headers=headers, **kwargs)

    def get_profile(self, username, headers=None, **kwargs):
        """GET /profiles/{username} 获取指定用户资料。"""
        return self.client.get(f"/profiles/{username}", headers=headers, **kwargs)

    def delete_profile(self, username, headers=None, **kwargs):
        """DELETE /profiles/{username} 删除指定用户。"""
        return self.client.delete(f"/profiles/{username}", headers=headers, **kwargs)

    def follow(self, username, headers=None, **kwargs):
        """POST /profiles/{username}/follow 关注用户。"""
        return self.client.post(f"/profiles/{username}/follow", headers=headers, **kwargs)

    def unfollow(self, username, headers=None, **kwargs):
        """DELETE /profiles/{username}/follow 取消关注。"""
        return self.client.delete(f"/profiles/{username}/follow", headers=headers, **kwargs)
