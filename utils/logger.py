"""日志组件：写文件 + 控制台，敏感头在调用方脱敏后传入。"""
import logging
import os

BASE_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
LOG_PATH = os.path.join(BASE_PATH, "log")
os.makedirs(LOG_PATH, exist_ok=True)


def _build_logger():
    lg = logging.getLogger("realworld_api_test")
    if lg.handlers:
        return lg
    lg.setLevel(logging.DEBUG)
    fmt = logging.Formatter(
        "[%(asctime)s][%(filename)s %(lineno)d][%(levelname)s]: %(message)s"
    )
    fh = logging.FileHandler(os.path.join(LOG_PATH, "run.log"), mode="a", encoding="UTF-8")
    fh.setFormatter(fmt)
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    ch.setLevel(logging.INFO)
    lg.addHandler(fh)
    lg.addHandler(ch)
    return lg


logger = _build_logger()
