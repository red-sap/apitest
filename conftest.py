"""根 conftest：全局客户端、登录身份与清理。

鉴权依赖：POST /users 注册 -> POST /users/login 拿 token -> Authorization: Token <token>。
session 级身份供各测试复用；账号在会话结束时做尽力清理（DELETE /profiles/{username}）。
"""
import secrets
import time

import pytest

from utils.rest_client import RestClient
from utils.config import get_config
from utils.logger import logger

_cfg = get_config()
BASE_URL = _cfg["app"]["base_url"]

# 本次会话创建过的账号（session 结束时尽力清理）
_CREATED_ACCOUNTS = []


@pytest.fixture(scope="session")
def api_client():
    return RestClient(BASE_URL)


def _register_and_login(client, prefix):
    """注册 + 登录一个唯一用户，返回 {username, email, password, token, user}。"""
    uniq = f"{prefix}_{int(time.time() * 1000)}_{secrets.token_hex(3)}"
    email = f"{uniq}@example.com"
    password = "Passw0rd!123"
    r = client.post("/users", json={"user": {"username": uniq, "email": email, "password": password}})
    assert r.status_code == 201, f"[fixture] 注册失败: {r.status_code} {r.text[:200]}"
    r2 = client.post("/users/login", json={"user": {"email": email, "password": password}})
    assert r2.status_code == 202, f"[fixture] 登录失败: {r2.status_code} {r2.text[:200]}"
    body = r2.json()["user"]
    info = {
        "username": uniq,
        "email": email,
        "password": password,
        "token": body["token"],
        "user": body,
    }
    _CREATED_ACCOUNTS.append(info)
    logger.info("[fixture] 已创建会话用户: %s", uniq)
    return info


@pytest.fixture(scope="session")
def test_user(api_client):
    return _register_and_login(api_client, "apitest_main")


@pytest.fixture(scope="session")
def second_user(api_client):
    return _register_and_login(api_client, "apitest_second")


@pytest.fixture
def auth_headers(test_user):
    """主身份鉴权头（function 作用域，便于单个用例覆盖）。"""
    return {"Authorization": f"Token {test_user['token']}"}


@pytest.fixture
def second_auth_headers(second_user):
    """第二身份鉴权头。"""
    return {"Authorization": f"Token {second_user['token']}"}


def pytest_sessionfinish(session, exitstatus):
    """会话结束：尽力删除本次注册的账号，避免残留。

    删除账号接口无归属校验，任一会话用户 token 均可删除任一账号；
    先删除其余账号，最后删除主账号自身。
    """
    client = RestClient(BASE_URL)
    accounts = list(_CREATED_ACCOUNTS)
    if not accounts:
        return
    deleter = accounts[-1]
    headers = {"Authorization": f"Token {deleter['token']}"}
    for info in accounts:
        try:
            r = client.delete(f"/profiles/{info['username']}", headers=headers)
            logger.info("[cleanup] 删除账号 %s -> %s", info["username"], r.status_code)
        except Exception as e:  # noqa: BLE001
            logger.warning("[cleanup] 删除账号 %s 失败: %s", info["username"], e)
