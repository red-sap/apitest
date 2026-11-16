"""标签接口测试。"""
import pytest

from utils.yaml_loader import load_yaml_for_parametrize
from utils.path import CASE_PATH
from utils.assertions import assert_common
from utils.logger import logger
from tests.api.tags.helpers import assert_tags_body


@pytest.mark.tags
@pytest.mark.smoke
@pytest.mark.parametrize("case", load_yaml_for_parametrize(CASE_PATH / "api/tags/list_tags.yaml"))
def test_list_tags(case, tags_api):
    resp = tags_api.list_tags()
    logger.info("标签列表响应: %s", resp.text[:300])
    expect = case["expect"]
    body = assert_common(resp, expect)
    assert_tags_body(body)
