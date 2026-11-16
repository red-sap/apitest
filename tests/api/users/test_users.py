"""用户注册 / 登录测试。"""
import pytest

from utils.yaml_loader import load_yaml_for_parametrize
from utils.case_utils import resolve_case_placeholders, resolve_fixture_placeholders
from utils.path import CASE_PATH
from utils.assertions import assert_common
from utils.logger import logger
from tests.api.users.helpers import assert_register_user


@pytest.mark.users
@pytest.mark.parametrize("case", load_yaml_for_parametrize(CASE_PATH / "api/users/register.yaml"))
def test_register(case, users_api, test_user, register_cleanup):
    case = resolve_case_placeholders(case, "register")
    case = resolve_fixture_placeholders(case, email=test_user["email"])
    payload = case["json"]
    resp = users_api.register(json=payload)
    logger.info("注册响应: %s", resp.text[:300])
    expect = case["expect"]
    body = assert_common(resp, expect)
    if expect["status_code"] == 201:
        assert_register_user(body, payload)
        register_cleanup.append(payload["user"]["username"])


@pytest.mark.users
@pytest.mark.parametrize("case", load_yaml_for_parametrize(CASE_PATH / "api/users/login.yaml"))
def test_login(case, users_api, test_user):
    case = resolve_case_placeholders(case, "login")
    case = resolve_fixture_placeholders(
        case, email=test_user["email"], password=test_user["password"]
    )
    resp = users_api.login(json=case["json"])
    logger.info("登录响应: %s", resp.text[:300])
    expect = case["expect"]
    body = assert_common(resp, expect)
    if expect.get("token_present"):
        assert body["user"]["email"] == case["json"]["user"]["email"]
        assert body["user"]["token"]
