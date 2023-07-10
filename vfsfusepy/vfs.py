from fuse import Operations
import git
import os
from typing import Optional, Dict, Any, List

import vfsfusepy.file_operations as file_operations
import vfsfusepy.git_operations as git_operations
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
        git_operations.add(self.repo, full_path)
        git_operations.commit(self.repo, "-m", f"create file {path}")
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
        git_operations.add(self.repo, full_path)
        git_operations.commit(self.repo, "-m", f"write file {path}")
        return size

    @handle_os_errors
    def truncate(self, path: str, length: int, fh: Optional[int] = None) -> int:
        full_path = file_path(self.repo.working_dir, path)
        file_operations.truncate(full_path, length, fh)
        if is_git_path(path):
            return 0

        git_operations.add(self.repo, full_path)
        git_operations.commit(self.repo, "-m", f"truncate file {path}")

    @handle_os_errors
    def unlink(self, path: str) -> None:
        full_path = file_path(self.repo.working_dir, path)
        os.unlink(full_path)
        if is_git_path(path):
            return

        git_operations.add(self.repo, full_path)
        git_operations.commit(self.repo, "-m", f"remove file {path}")

    @handle_os_errors
    def mkdir(self, path: str, mode: int) -> None:
        full_path = file_path(self.repo.working_dir, path)
        os.mkdir(full_path, mode)
        if is_git_path(path):
            return

        git_operations.add(self.repo, full_path)
        git_operations.commit(self.repo, "-m", f"create directory {path}")

    @handle_os_errors
    def rmdir(self, path: str) -> None:
        full_path = file_path(self.repo.working_dir, path)
        if os.path.exists(full_path):
            os.rmdir(full_path)

    @handle_os_errors
    def rename(self, old_path: str, new_path: str) -> None:
        old_full_path = file_path(self.repo.working_dir, old_path)
        new_full_path = file_path(self.repo.working_dir, new_path)
        os.rename(old_full_path, new_full_path)
        if is_git_path(old_path) and is_git_path(new_path):
            return
        if is_git_path(old_path):
            git_operations.add(self.repo, new_full_path)
            git_operations.commit(self.repo, "-m", f"create file {new_path}")
            return
        if is_git_path(new_path):
            self.repo.git.rm(old_full_path)
            git_operations.commit(self.repo, "-m", f"remove file {old_path}")
            return

        git_operations.add(self.repo, old_full_path)
        git_operations.add(self.repo, new_full_path)
        git_operations.commit(self.repo, "-m", f"rename from {old_path} to {new_path}")

    @handle_os_errors
    def access(self, path: str, mode: int) -> None:
        file_operations.access(file_path(self.repo.working_dir, path), mode)

    @handle_os_errors
    def chmod(self, path: str, mode: int) -> None:
        full_path = file_path(self.repo.working_dir, path)
        os.chmod(full_path, mode)
        if is_git_path(path):
            return

        git_operations.add(self.repo, full_path)
        git_operations.commit(self.repo, "-m", f"change mode of {path}")

    @handle_os_errors
    def readlink(self, path: str) -> str:
        full_path = file_path(self.repo.working_dir, path)
        pathname = os.readlink(full_path)
        if pathname.startswith("/"):
            # Path name is absolute, sanitize it.
            return os.path.relpath(pathname, self.repo.working_dir)
        return pathname

    @handle_os_errors
    def mknod(self, path: str, mode: int, dev: int) -> None:
        os.mknod(file_path(self.repo.working_dir, path), mode, dev)

    @handle_os_errors
    def symlink(self, target: str, source: str) -> None:
        full_path = file_path(self.repo.working_dir, target)
        os.symlink(file_path(self.repo.working_dir, source), full_path)
        if is_git_path(target):
            return

        git_operations.add(self.repo, full_path)
        git_operations.commit(self.repo, "-m", f"create file {target}")

    @handle_os_errors
    def link(self, target: str, source: str) -> None:
        full_path = file_path(self.repo.working_dir, target)
        os.link(file_path(self.repo.working_dir, source), full_path)
        if is_git_path(target):
            return

        git_operations.add(self.repo, full_path)
        git_operations.commit(self.repo, "-m", f"create file {target}")
