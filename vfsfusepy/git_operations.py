import git


def add(repo: git.Repo, path: str) -> None:
    if repo.git.status("--porcelain"):
        repo.git.add(path)


def commit(repo: git.Repo, mode: str, message: str) -> None:
    if repo.git.status("--porcelain"):
        repo.git.commit(mode, message)
