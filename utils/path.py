"""项目路径常量，供各模块统一引用。"""
from pathlib import Path

UTIL_PATH = Path(__file__).parent
BASE_PATH = UTIL_PATH.parent
API_PATH = BASE_PATH / "apis"
CASE_PATH = BASE_PATH / "cases"
REPORT_PATH = BASE_PATH / "reports"
SPEC_PATH = BASE_PATH / "specs"
