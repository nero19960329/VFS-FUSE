import errno
from fuse import FuseOSError
from loguru import logger
import os
import traceback
from typing import Any, Callable


def file_path(working_dir: str, path: str) -> str:
    return os.path.join(working_dir, path.lstrip("/"))


def is_git_path(path: str) -> bool:
    return path.lstrip("/").startswith(".git")


def handle_os_errors(func: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except OSError as e:
            raise FuseOSError(e.errno) from e
        except Exception as e:
            logger.error(traceback.format_exc())
            raise FuseOSError(errno.EACCES) from e

    return wrapper
