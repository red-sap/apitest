"""HTTP 客户端：基于 requests.Session，统一处理 JSON/params/headers 并做脱敏日志。"""
import requests

from utils.logger import logger

# 需要脱敏的请求头/响应字段
_SENSITIVE_HEADERS = {"authorization", "cookie", "set-cookie", "x-api-key", "token"}


def _redact_headers(headers):
    if not headers:
        return headers
    out = {}
    for k, v in headers.items():
        if k.lower() in _SENSITIVE_HEADERS:
            out[k] = "<redacted>"
        else:
            out[k] = v
    return out


class RestClient:
    """封装 requests.Session，api_root_url 为接口根地址（含 basePath）。"""

    def __init__(self, api_root_url):
        self.api_root_url = api_root_url.rstrip("/")
        self.session = requests.Session()

    def get(self, url, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url, data=None, json=None, **kwargs):
        return self.request("POST", url, data=data, json=json, **kwargs)

    def put(self, url, data=None, json=None, **kwargs):
        return self.request("PUT", url, data=data, json=json, **kwargs)

    def patch(self, url, data=None, json=None, **kwargs):
        return self.request("PATCH", url, data=data, json=json, **kwargs)

    def delete(self, url, **kwargs):
        return self.request("DELETE", url, **kwargs)

    def request(self, method, url, data=None, json=None, params=None, headers=None, **kwargs):
        full_url = self.api_root_url + url
        logger.info(
            "请求: %s %s params=%s headers=%s",
            method, full_url, params, _redact_headers(headers),
        )
        kwargs.setdefault("timeout", (5, 30))
        resp = self.session.request(
            method, full_url, data=data, json=json, params=params, headers=headers, **kwargs
        )
        logger.info(
            "响应: %s %s status=%s",
            method, full_url, resp.status_code,
        )
        return resp
