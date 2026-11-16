"""当前用户接口测试。"""
import pytest

from utils.yaml_loader import load_yaml_for_parametrize
from utils.case_utils import resolve_case_placeholders, resolve_fixture_placeholders
from utils.path import CASE_PATH
from utils.assertions import assert_common
from utils.logger import logger
from tests.api.user.helpers import assert_current_user


@pytest.mark.user
@pytest.mark.parametrize("case", load_yaml_for_parametrize(CASE_PATH / "api/user/get_current_user.yaml"))
def test_get_current_user(case, user_api, auth_headers, test_user):
    expect = case["expect"]
    headers = None if case.get("no_auth") else auth_headers
    resp = user_api.get_current_user(headers=headers)
    logger.info("获取当前用户响应: %s", resp.text[:300])
    body = assert_common(resp, expect)
    if expect["status_code"] == 200:
        assert_current_user(body, test_user)
        assert "token" not in body, "GET /user 响应不应包含 token"


@pytest.mark.user
@pytest.mark.parametrize("case", load_yaml_for_parametrize(CASE_PATH / "api/user/update_user.yaml"))
def test_update_user(case, user_api, auth_headers, test_user):
    case = resolve_case_placeholders(case, "update_user")
    case = resolve_fixture_placeholders(case, email=test_user["email"])
    resp = user_api.update_user(json=case["json"], headers=auth_headers)
    logger.info("更新当前用户响应: %s", resp.text[:300])
    expect = case["expect"]
    body = assert_common(resp, expect)
    if expect["status_code"] == 200:
        assert body["bio"] == case["json"]["user"]["bio"]
        assert body["email"] == test_user["email"]
