"""用户资料 / 关注模块 conftest：Api fixture、临时用户与关注链准备。"""
import secrets
import time

import pytest

from apis.profiles_api import ProfilesApi
from utils.logger import logger


@pytest.fixture
def profiles_api(api_client):
    return ProfilesApi(api_client)


@pytest.fixture
def profile_cleanup(api_client, test_user):
    """记录创建资料用例产生的用户名，测试后尽力删除（释放空 email 唯一约束）。"""
    created = []
    yield created
    headers = {"Authorization": f"Token {test_user['token']}"}
    for username in created:
        try:
            api_client.delete(f"/profiles/{username}", headers=headers)
        except Exception as e:  # noqa: BLE001
            logger.warning("[cleanup] 删除资料用户 %s 失败: %s", username, e)


@pytest.fixture
def throwaway_user(api_client, test_user):
    """注册一个临时用户供删除资料用例使用，测试后若仍在则尽力删除。"""
    uniq = f"apitest_tmp_{int(time.time() * 1000)}_{secrets.token_hex(3)}"
    r = api_client.post(
        "/users",
        json={"user": {"username": uniq, "email": f"{uniq}@example.com", "password": "Passw0rd!123"}},
    )
    assert r.status_code == 201, f"准备临时用户失败: {r.status_code} {r.text[:200]}"
    yield {"username": uniq}
    headers = {"Authorization": f"Token {test_user['token']}"}
    try:
        api_client.delete(f"/profiles/{uniq}", headers=headers)
    except Exception as e:  # noqa: BLE001
        logger.warning("[cleanup] 删除临时用户 %s 失败: %s", uniq, e)


@pytest.fixture
def follow_cleanup(profiles_api, auth_headers):
    """记录关注关系，测试后尽力取消关注，保持可重复运行。"""
    targets = []
    yield targets
    for target in targets:
        try:
            profiles_api.unfollow(target, headers=auth_headers)
        except Exception as e:  # noqa: BLE001
            logger.warning("[cleanup] 取消关注 %s 失败: %s", target, e)


@pytest.fixture
def followed_user(profiles_api, auth_headers, second_user, follow_cleanup):
    """前置：主身份先关注第二用户，yield 被关注用户名；测试后由 follow_cleanup 清理。"""
    target = second_user["username"]
    r = profiles_api.follow(target, headers=auth_headers)
    assert r.status_code == 200, f"准备关注失败: {r.status_code} {r.text[:200]}"
    follow_cleanup.append(target)
    return target
