import os
from typing import Optional, Dict, Any, List


def _getattr(path: str, fh: Optional[int] = None) -> Dict[str, Any]:
    st = os.lstat(path)
    return {
        key: getattr(st, key)
        for key in (
            "st_atime",
            "st_ctime",
            "st_gid",
            "st_mode",
            "st_mtime",
            "st_nlink",
            "st_size",
            "st_uid",
        )
    }


def readdir(path: str, fh: Optional[int] = None) -> List[str]:
    dirents = [".", ".."]
    if os.path.isdir(path):
        dirents.extend(os.listdir(path))
    return dirents


def create(path: str, mode: int) -> int:
    return os.open(path, os.O_WRONLY | os.O_CREAT, mode)


def read(path: str, size: int, offset: int, fh: int) -> bytes:
    with open(path, "rb") as f:
        f.seek(offset)
        return f.read(size)


def write(path: str, data: bytes, offset: int, fh: int) -> int:
    with open(path, "rb+") as f:
        f.seek(offset)
        return f.write(data)


def truncate(path: str, length: int, fh: Optional[int] = None) -> None:
    with open(path, "rb+") as f:
        f.truncate(length)


def access(path: str, mode: int) -> None:
    if not os.access(path, mode):
        raise PermissionError(path)


def readlink(path: str) -> str:
    pathname = os.readlink(path)
    if pathname.startswith("/"):
        # Path name is absolute, sanitize it.
        return os.path.relpath(pathname, os.path.dirname(path))
    else:
        return pathname


def statfs(path: str) -> Dict[str, Any]:
    stv = os.statvfs(path)
    return {
        key: getattr(stv, key)
        for key in (
            "f_bavail",
            "f_bfree",
            "f_blocks",
            "f_bsize",
            "f_favail",
            "f_ffree",
            "f_files",
            "f_flag",
            "f_frsize",
            "f_namemax",
        )
    }
