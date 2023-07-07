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
            if path.lstrip("/").startswith(".git"):
                return 0
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
        if path.lstrip("/").startswith(".git"):
            os.lseek(fh, offset, os.SEEK_SET)
            return os.write(fh, data)

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
        if path.lstrip("/").startswith(".git"):
            full_path = os.path.join(self.repo.working_dir, path.lstrip("/"))
            with open(full_path, "r+") as f:
                f.truncate(length)
            return

        try:
            with open(f"{self.repo.working_dir}{path}", "rb+") as f:
                f.truncate(length)
        except FileNotFoundError as e:
            raise FuseOSError(errno.ENOENT) from e

    def unlink(self, path: str) -> None:
        file_path = os.path.join(self.repo.working_dir, path.lstrip("/"))
        try:
            os.unlink(file_path)
            if path.lstrip("/").startswith(".git"):
                return
            self.repo.git.rm(file_path)
            self.repo.git.commit("-m", f"remove file {path}")
        except Exception as e:
            logger.error(f"Failed to remove file: {file_path}. Error: {str(e)}")
            raise FuseOSError(errno.EACCES) from e

    def mkdir(self, path: str, mode: int) -> None:
        dir_path = os.path.join(self.repo.working_dir, path.lstrip("/"))
        gitkeep_path = os.path.join(dir_path, ".gitkeep")
        try:
            os.mkdir(dir_path, mode)
            if path.lstrip("/").startswith(".git"):
                return
            # Create .gitkeep file to track empty directories in Git
            with open(gitkeep_path, "w") as f:
                pass
            self.repo.git.add(dir_path)
            self.repo.git.commit("-m", f"create directory {path}")
        except Exception as e:
            logger.error(f"Failed to create directory: {dir_path}. Error: {str(e)}")
            raise FuseOSError(errno.EACCES) from e

    def rmdir(self, path: str) -> None:
        return

    def rename(self, old_path: str, new_path: str) -> None:
        old_full_path = os.path.join(self.repo.working_dir, old_path.lstrip("/"))
        new_full_path = os.path.join(self.repo.working_dir, new_path.lstrip("/"))

        if old_path.lstrip("/").startswith(".git") and new_path.lstrip("/").startswith(
            ".git"
        ):
            os.rename(old_full_path, new_full_path)
            return
        elif old_path.lstrip("/").startswith(".git"):
            # This is equivalent to creating a new file or directory at new_path
            os.rename(old_full_path, new_full_path)
            self.repo.git.add(new_full_path)
            self.repo.git.commit("-m", f"create file {new_path}")
            return
        elif new_path.lstrip("/").startswith(".git"):
            # This is equivalent to deleting a file or directory at old_path
            os.rename(old_full_path, new_full_path)
            self.repo.git.rm(old_full_path)
            self.repo.git.commit("-m", f"remove file {old_path}")
            return

        try:
            # Check if the old file/directory is tracked by Git
            old_path_strip = old_path.lstrip("/")
            is_tracked = any(
                path.startswith(old_path_strip)
                for path in self.repo.git.ls_files().split("\n")
            )
            if is_tracked:
                self.repo.git.mv(old_full_path, new_full_path)
                self.repo.git.commit("-m", f"rename from {old_path} to {new_path}")
            else:
                os.rename(old_full_path, new_full_path)
        except Exception as e:
            logger.error(
                f"Failed to rename: {old_full_path} to {new_full_path}. Error: {str(e)}"
            )
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
