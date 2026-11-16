"""测试用例占位符解析工具。

占位符规则：
  __UUID__            -> API_Test_<毫秒时间戳>_<endpoint>_<随机串>
  __<KEY>__           -> extra[KEY]（KEY 需全大写，如 __AUTHOR__）
  __fixture_<name>__  -> fixtures[name]（fixture 层注入的下游数据）

只遍历 case 的 params / data / json 三个键，不修改原始参数化数据。
"""
import copy
import secrets
import time


def _new_uuid(endpoint_name=""):
    return f"API_Test_{int(time.time() * 1000)}_{endpoint_name}_{secrets.token_hex(3)}"


def _walk(obj, mapper):
    if isinstance(obj, dict):
        return {k: _walk(v, mapper) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_walk(v, mapper) for v in obj]
    if isinstance(obj, str):
        return mapper(obj)
    return obj


def resolve_case_placeholders(case, endpoint_name="", **extra):
    """解析 case 中的 __UUID__ 与 __KEY__ 占位符，返回新的 case dict。"""
    case = copy.deepcopy(case)
    uuid_value = _new_uuid(endpoint_name)
    key_map = {str(k).upper(): v for k, v in extra.items()}

    def mapper(value):
        for key, val in key_map.items():
            value = value.replace(f"__{key}__", str(val))
        value = value.replace("__UUID__", uuid_value)
        return value

    for field in ("params", "data", "json"):
        if case.get(field) is not None:
            case[field] = _walk(case[field], mapper)
    return case


def resolve_fixture_placeholders(case, **fixtures):
    """将 case 中的 __fixture_<name>__ 占位符替换为 fixture 值，返回新的 case dict。"""
    case = copy.deepcopy(case)

    def mapper(value):
        for key, val in fixtures.items():
            value = value.replace(f"__fixture_{key}__", str(val))
        return value

    for field in ("params", "data", "json"):
        if case.get(field) is not None:
            case[field] = _walk(case[field], mapper)
    return case
