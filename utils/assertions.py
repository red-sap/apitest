"""通用断言工具。"""
from utils.logger import logger


def safe_json(resp):
    """安全解析响应 JSON；空响应 / 非 JSON（如 500 HTML 调试页）返回 None。"""
    text = (resp.text or "").strip()
    if not text:
        return None
    try:
        return resp.json()
    except Exception:
        return None


def assert_status(resp, expected, msg=""):
    actual = resp.status_code
    logger.info("[断言] status_code | 期望: %s | 实际: %s", expected, actual)
    assert actual == expected, (
        f"{msg} 期望状态码 {expected}，实际 {actual}，响应体: {resp.text[:300]}"
    )


def assert_common(resp, expect):
    """按 expect 字段做通用断言，返回解析后的响应体（或 None）。"""
    assert_status(resp, expect["status_code"])
    body = safe_json(resp)

    if expect.get("body_empty"):
        assert body is None, f"期望空响应体，实际: {resp.text[:200]}"
        return body

    if expect.get("body_has_key"):
        assert isinstance(body, dict), f"期望 JSON 对象，实际: {resp.text[:200]}"
        assert expect["body_has_key"] in body, f"响应缺少键 {expect['body_has_key']}: {body}"

    if expect.get("body_is_list"):
        assert isinstance(body, list), f"期望 JSON 数组，实际: {resp.text[:200]}"

    if expect.get("has_errors"):
        assert isinstance(body, dict) and "errors" in body, f"期望 errors 结构，实际: {body}"

    if expect.get("token_present"):
        assert isinstance(body, dict) and body.get("user", {}).get("token"), "登录成功应返回 token"

    return body
