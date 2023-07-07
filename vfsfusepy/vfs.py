from fuse import Operations
import git
import os
from typing import Optional, Dict, Any, List

import vfsfusepy.file_operations as file_operations
from vfsfusepy.utils import is_git_path, handle_os_errors, file_path


class VFS(Operations):
    def __init__(self, git_dir: str):
        self.repo = git.Repo.init(git_dir)

    @handle_os_errors
    def getattr(self, path: str, fh: Optional[int] = None) -> Dict[str, Any]:
        return file_operations._getattr(
            file_path(self.repo.working_dir, path),
            fh,
        )

    @handle_os_errors
    def readdir(self, path: str, fh: Optional[int] = None) -> List[str]:
        return file_operations.readdir(
            file_path(self.repo.working_dir, path),
            fh,
        )

    @handle_os_errors
    def create(self, path: str, mode: int) -> int:
        full_path = file_path(self.repo.working_dir, path)
        file_operations.create(full_path, mode)
        if is_git_path(path):
            return 0
        self.repo.git.add(full_path)
        self.repo.git.commit("-m", f"create file {path}")
        return 0

    @handle_os_errors
    def read(self, path: str, size: int, offset: int, fh: int) -> bytes:
        return file_operations.read(
            file_path(self.repo.working_dir, path), size, offset, fh
        )

    @handle_os_errors
    def write(self, path: str, data: bytes, offset: int, fh: int) -> int:
        full_path = file_path(self.repo.working_dir, path)
        size = file_operations.write(full_path, data, offset, fh)
        if is_git_path(path):
            return size

        full_path = file_path(self.repo.working_dir, path)
        self.repo.git.add(full_path)
        self.repo.git.commit("-m", f"write file {path}")
        return size

    @handle_os_errors
    def truncate(self, path: str, length: int, fh: Optional[int] = None) -> int:
        file_operations.truncate(file_path(self.repo.working_dir, path), length, fh)

    @handle_os_errors
    def unlink(self, path: str) -> None:
        full_path = file_path(self.repo.working_dir, path)
        file_operations.unlink(full_path)
        if is_git_path(path):
            return

        self.repo.git.rm(full_path)
        self.repo.git.commit("-m", f"remove file {path}")

    @handle_os_errors
    def mkdir(self, path: str, mode: int) -> None:
        full_path = file_path(self.repo.working_dir, path)
        file_operations.mkdir(full_path, mode)
        if is_git_path(path):
            return

        gitkeep_path = os.path.join(full_path, ".gitkeep")
        # Create .gitkeep file to track empty directories in Git
        with open(gitkeep_path, "w") as f:
            pass
        self.repo.git.add(full_path)
        self.repo.git.commit("-m", f"create directory {path}")

    @handle_os_errors
    def rmdir(self, path: str) -> None:
        full_path = file_path(self.repo.working_dir, path)
        if os.path.exists(full_path):
            file_operations.rmdir(full_path)

    @handle_os_errors
    def rename(self, old_path: str, new_path: str) -> None:
        old_full_path = file_path(self.repo.working_dir, old_path)
        new_full_path = file_path(self.repo.working_dir, new_path)
        file_operations.rename(old_full_path, new_full_path)
        if is_git_path(old_path) and is_git_path(new_path):
            return
        if is_git_path(old_path):
            self.repo.git.add(new_full_path)
            self.repo.git.commit("-m", f"create file {new_path}")
            return
        if is_git_path(new_path):
            self.repo.git.rm(old_full_path)
            self.repo.git.commit("-m", f"remove file {old_path}")
            return

        self.repo.git.add(old_full_path)
        self.repo.git.add(new_full_path)
        self.repo.git.commit("-m", f"rename from {old_path} to {new_path}")
