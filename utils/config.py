"""全局配置读取层。

从 config.yaml 读取，支持环境变量覆盖（优先级：环境变量 > config.yaml > 内置默认值）。
"""
import copy
import os

import yaml

from utils.path import BASE_PATH

CONFIG_FILE = BASE_PATH / "config.yaml"

_DEFAULTS = {
    "app": {
        "base_url": "http://127.0.0.1:8000/api",
    },
    "spec": {
        "swagger_url": "http://127.0.0.1:8000/swagger/?format=openapi",
    },
}

_ENV_MAP = {
    "APP_BASE_URL": ("app", "base_url"),
    "SWAGGER_URL": ("spec", "swagger_url"),
}


def _deep_update(target, source):
    for key, value in source.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            _deep_update(target[key], value)
        else:
            target[key] = copy.deepcopy(value)
    return target


def _set_nested(data, path, value):
    for key in path[:-1]:
        data = data.setdefault(key, {})
    data[path[-1]] = value


def load_config():
    data = copy.deepcopy(_DEFAULTS)
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, encoding="utf-8") as f:
            user_cfg = yaml.safe_load(f) or {}
        _deep_update(data, user_cfg)
    for env_key, path in _ENV_MAP.items():
        val = os.environ.get(env_key)
        if val:
            _set_nested(data, path, val)
    return data


_config = None


def get_config():
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reload_config():
    global _config
    _config = load_config()
    return _config
