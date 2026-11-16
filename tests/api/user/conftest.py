"""当前用户模块 conftest。"""
import pytest

from apis.user_api import UserApi


@pytest.fixture
def user_api(api_client):
    return UserApi(api_client)
