"""标签模块 conftest。"""
import pytest

from apis.tags_api import TagsApi


@pytest.fixture
def tags_api(api_client):
    return TagsApi(api_client)
