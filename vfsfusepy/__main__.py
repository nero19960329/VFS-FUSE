#!/usr/bin/env python3
from argparse import ArgumentParser
import errno
from fuse import FUSE, FuseOSError, Operations
import git
from loguru import logger
import os
from typing import Optional, Dict, Any, List


class VFS(Operations):
    def __init__(self, git_dir: str):
        self.repo = git.Repo.init(git_dir)

    def getattr(self, path: str, fh: Optional[int] = None) -> Dict[str, Any]:
        try:
            st = os.lstat(f"{self.repo.working_dir}{path}")
        except OSError as e:
            raise FuseOSError(e.errno) from e

        return {
            k: getattr(st, k)
            for k in (
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

    def readdir(self, path: str, fh: int) -> List[str]:
        return [".", ".."] + os.listdir(f"{self.repo.working_dir}{path}")

    def create(self, path: str, mode: int) -> int:
        file_path = os.path.join(self.repo.working_dir, path.lstrip("/"))
        try:
            fd = os.open(file_path, os.O_WRONLY | os.O_CREAT, mode)
            os.close(fd)
            self.repo.git.add(file_path)
            self.repo.git.commit("-m", f"create file {path}")
            return 0
        except Exception as e:
            logger.error(f"Failed to create file: {file_path}. Error: {str(e)}")
            raise FuseOSError(errno.EACCES) from e

    def read(self, path: str, size: int, offset: int, fh: int) -> bytes:
        try:
            with open(f"{self.repo.working_dir}{path}", "rb") as f:
                f.seek(offset)
                return f.read(size)
        except FileNotFoundError as e:
            raise FuseOSError(errno.ENOENT) from e

    def write(self, path: str, data: bytes, offset: int, fh: int) -> int:
        file_path = os.path.join(self.repo.working_dir, path.lstrip("/"))
        try:
            with open(file_path, "wb") as f:
                f.seek(offset)
                f.write(data)
            self.repo.git.add(file_path)
            self.repo.git.commit("-m", f"update file {path}")
            return len(data)
        except Exception as e:
            logger.error(f"Failed to write file: {file_path}. Error: {str(e)}")
            raise FuseOSError(errno.EACCES) from e

    def truncate(self, path: str, length: int, fh: Optional[int] = None) -> None:
        try:
            with open(f"{self.repo.working_dir}{path}", "rb+") as f:
                f.truncate(length)
        except FileNotFoundError as e:
            raise FuseOSError(errno.ENOENT) from e

    def unlink(self, path: str) -> None:
        file_path = os.path.join(self.repo.working_dir, path.lstrip("/"))
        try:
            os.unlink(file_path)
            self.repo.git.rm(file_path)
            self.repo.git.commit("-m", f"remove file {path}")
        except Exception as e:
            logger.error(f"Failed to remove file: {file_path}. Error: {str(e)}")
            raise FuseOSError(errno.EACCES) from e


def parse_args():
    parser = ArgumentParser(
        description="A versioned file system based on FUSE and Git."
    )
    parser.add_argument(
        "git_dir", type=str, help="The directory of the git repository."
    )
    parser.add_argument(
        "mount_point", type=str, help="The mount point of the file system."
    )
    return parser.parse_args()


def main():
    args = parse_args()
    FUSE(VFS(args.git_dir), args.mount_point, foreground=True)


if __name__ == "__main__":
    main()
