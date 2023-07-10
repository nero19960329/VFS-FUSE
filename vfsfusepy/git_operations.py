import git


def commit(repo: git.Repo, mode: str, message: str) -> None:
    if repo.git.status("--porcelain"):
        repo.git.commit(mode, message)
