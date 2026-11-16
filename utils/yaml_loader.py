"""YAML 用例加载工具。"""
import yaml

from utils.logger import logger


def load_yaml_for_parametrize(file_path):
    """加载参数化用例文件，返回顶层 cases 列表。"""
    logger.info("加载用例文件: %s", file_path)
    with open(file_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("cases", [])


def load_yaml(file_path):
    with open(file_path, encoding="utf-8") as f:
        return yaml.safe_load(f)
