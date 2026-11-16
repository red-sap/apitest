"""用户资料 / 关注接口测试。"""
import pytest

from utils.yaml_loader import load_yaml_for_parametrize
from utils.case_utils import resolve_case_placeholders
from utils.path import CASE_PATH
from utils.assertions import assert_common
from utils.logger import logger
from tests.api.profiles.helpers import assert_profile_body


@pytest.mark.profiles
@pytest.mark.parametrize("case", load_yaml_for_parametrize(CASE_PATH / "api/profiles/list_profiles.yaml"))
def test_list_profiles(case, profiles_api, auth_headers):
    resp = profiles_api.list_profiles(headers=auth_headers)
    logger.info("资料列表响应: %s", resp.text[:300])
    expect = case["expect"]
    assert_common(resp, expect)  # 200 + has_errors（实现缺陷）


@pytest.mark.profiles
@pytest.mark.parametrize("case", load_yaml_for_parametrize(CASE_PATH / "api/profiles/get_profile.yaml"))
def test_get_profile(case, profiles_api, auth_headers, test_user):
    expect = case["expect"]
    headers = None if case.get("no_auth") else auth_headers
    resp = profiles_api.get_profile(test_user["username"], headers=headers)
    logger.info("获取资料响应: %s", resp.text[:300])
    body = assert_common(resp, expect)
    if expect["status_code"] == 200:
        assert_profile_body(body)
        assert body["username"] == test_user["username"]


@pytest.mark.profiles
@pytest.mark.parametrize("case", load_yaml_for_parametrize(CASE_PATH / "api/profiles/create_profile.yaml"))
def test_create_profile(case, profiles_api, auth_headers, profile_cleanup):
    case = resolve_case_placeholders(case, "create_profile")
    resp = profiles_api.create_profile(json=case["json"], headers=auth_headers)
    logger.info("创建资料响应: %s", resp.text[:300])
    expect = case["expect"]
    body = assert_common(resp, expect)
    if expect["status_code"] == 201:
        assert body["username"] == case["json"]["username"]
        profile_cleanup.append(case["json"]["username"])


@pytest.mark.profiles
@pytest.mark.parametrize("case", load_yaml_for_parametrize(CASE_PATH / "api/profiles/delete_profile.yaml"))
def test_delete_profile(case, profiles_api, auth_headers, throwaway_user):
    resp = profiles_api.delete_profile(throwaway_user["username"], headers=auth_headers)
    logger.info("删除资料响应: %s", resp.text[:300])
    expect = case["expect"]
    assert_common(resp, expect)  # 204
    check = profiles_api.get_profile(throwaway_user["username"], headers=auth_headers)
    assert check.status_code == 404, f"删除后仍可访问: {check.status_code}"


@pytest.mark.profiles
@pytest.mark.parametrize("case", load_yaml_for_parametrize(CASE_PATH / "api/profiles/follow.yaml"))
def test_follow(case, profiles_api, auth_headers, test_user, second_user, follow_cleanup):
    expect = case["expect"]
    target = test_user["username"] if case.get("self_follow") else second_user["username"]
    resp = profiles_api.follow(target, headers=auth_headers)
    logger.info("关注响应: %s", resp.text[:300])
    body = assert_common(resp, expect)
    if expect["status_code"] == 200:
        assert body["profile"]["following"] is True
        follow_cleanup.append(target)


@pytest.mark.profiles
@pytest.mark.parametrize("case", load_yaml_for_parametrize(CASE_PATH / "api/profiles/unfollow.yaml"))
def test_unfollow(case, profiles_api, auth_headers, followed_user):
    resp = profiles_api.unfollow(followed_user, headers=auth_headers)
    logger.info("取消关注响应: %s", resp.text[:300])
    expect = case["expect"]
    body = assert_common(resp, expect)
    if expect["status_code"] == 200:
        assert body["profile"]["following"] is False
