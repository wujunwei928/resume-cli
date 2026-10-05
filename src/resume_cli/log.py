"""日志体系：结果走 stdout，日志一律走 stderr，保证管道重定向纯净。"""

import logging
import sys

_FORMAT = "%(levelname)s %(message)s"


def setup_logging(verbose: bool = False) -> None:
    """初始化根日志器；verbose 时升 DEBUG（含 prompt 摘要）。"""
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter(_FORMAT))
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(logging.DEBUG if verbose else logging.INFO)
