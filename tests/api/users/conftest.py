"""用户注册 / 登录模块 conftest：Api fixture 与注册用例清理。"""
import pytest

from apis.users_api import UsersApi
from utils.logger import logger


@pytest.fixture
def users_api(api_client):
    return UsersApi(api_client)


@pytest.fixture
def register_cleanup(api_client, test_user):
    """记录注册用例创建的用户名，测试后用主身份尽力删除（删除账号接口无归属校验）。"""
    created = []
    yield created
    headers = {"Authorization": f"Token {test_user['token']}"}
    for username in created:
        try:
            api_client.delete(f"/profiles/{username}", headers=headers)
        except Exception as e:  # noqa: BLE001
            logger.warning("[cleanup] 删除注册用户 %s 失败: %s", username, e)
