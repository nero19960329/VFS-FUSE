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


def unlink(path: str) -> None:
    os.unlink(path)


def mkdir(path: str, mode: int) -> None:
    os.mkdir(path, mode)


def rmdir(path: str) -> None:
    os.rmdir(path)


def rename(old_path: str, new_path: str) -> None:
    os.rename(old_path, new_path)
