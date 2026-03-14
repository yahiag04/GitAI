from dataclasses import dataclass


@dataclass(slots=True)
class PullRequestInput:
    owner: str
    repo: str
    title: str
    head: str
    base: str
    body: str | None = None


@dataclass(slots=True)
class GitHubService:
    def create_repo(self, name: str, visibility: str = "public") -> None:
        raise NotImplementedError("TODO: create a GitHub repository.")

    def create_pull_request(self, input_data: PullRequestInput) -> None:
        raise NotImplementedError("TODO: open a pull request on GitHub.")

    def list_branches(self, owner: str, repo: str) -> list[str]:
        raise NotImplementedError("TODO: fetch branches from GitHub.")

    def list_commits(self, owner: str, repo: str) -> list[str]:
        raise NotImplementedError("TODO: fetch commits from GitHub.")


def create_github_service() -> GitHubService:
    return GitHubService()

