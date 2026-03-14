import os
from dataclasses import dataclass, field
from typing import Optional

from github import Github, GithubException, Auth


@dataclass
class PullRequestInput:
    owner: str
    repo: str
    title: str
    head: str
    base: str
    body: str | None = None


@dataclass
class RepoInfo:
    name: str
    full_name: str
    clone_url: str
    ssh_url: str
    html_url: str


@dataclass
class PullRequestInfo:
    number: int
    title: str
    html_url: str
    state: str


@dataclass
class GitHubService:
    _client: Optional[Github] = field(default=None, repr=False)
    _token: Optional[str] = field(default=None, repr=False)

    def __post_init__(self) -> None:
        self._token = os.environ.get("GITHUB_TOKEN")

    def _get_client(self) -> Github:
        """Get or initialize the GitHub client."""
        if self._client is None:
            if self._token is None:
                raise ValueError(
                    "GitHub token not found. Set the GITHUB_TOKEN environment variable."
                )
            auth = Auth.Token(self._token)
            self._client = Github(auth=auth)
        return self._client

    def create_repo(
        self,
        name: str,
        visibility: str = "public",
        description: str = "",
    ) -> RepoInfo:
        """Create a GitHub repository."""
        client = self._get_client()
        user = client.get_user()

        private = visibility == "private"

        try:
            repo = user.create_repo(
                name=name,
                description=description,
                private=private,
                auto_init=False,
            )
            return RepoInfo(
                name=repo.name,
                full_name=repo.full_name,
                clone_url=repo.clone_url,
                ssh_url=repo.ssh_url,
                html_url=repo.html_url,
            )
        except GithubException as e:
            if e.status == 422:
                raise ValueError(f"Repository '{name}' already exists.")
            raise

    def create_pull_request(self, input_data: PullRequestInput) -> PullRequestInfo:
        """Open a pull request on GitHub."""
        client = self._get_client()

        repo = client.get_repo(f"{input_data.owner}/{input_data.repo}")

        try:
            pr = repo.create_pull(
                title=input_data.title,
                body=input_data.body or "",
                head=input_data.head,
                base=input_data.base,
            )
            return PullRequestInfo(
                number=pr.number,
                title=pr.title,
                html_url=pr.html_url,
                state=pr.state,
            )
        except GithubException as e:
            if e.status == 422:
                raise ValueError(
                    f"Cannot create PR: {e.data.get('message', 'Unknown error')}"
                )
            raise

    def list_branches(self, owner: str, repo: str) -> list[str]:
        """Fetch branches from GitHub."""
        client = self._get_client()
        repository = client.get_repo(f"{owner}/{repo}")
        return [branch.name for branch in repository.get_branches()]

    def list_commits(
        self,
        owner: str,
        repo: str,
        branch: str | None = None,
        limit: int = 10,
    ) -> list[dict]:
        """Fetch commits from GitHub."""
        client = self._get_client()
        repository = client.get_repo(f"{owner}/{repo}")

        kwargs = {}
        if branch:
            kwargs["sha"] = branch

        commits = []
        for commit in repository.get_commits(**kwargs)[:limit]:
            commits.append({
                "sha": commit.sha[:7],
                "message": commit.commit.message.split("\n")[0],
                "author": commit.commit.author.name,
            })
        return commits

    def get_authenticated_user(self) -> str:
        """Get the username of the authenticated user."""
        client = self._get_client()
        return client.get_user().login

    def delete_repo(self, owner: str, repo: str) -> str:
        """Delete a GitHub repository."""
        client = self._get_client()
        repository = client.get_repo(f"{owner}/{repo}")
        repository.delete()
        return f"Deleted repository {owner}/{repo}"


def create_github_service() -> GitHubService:
    return GitHubService()

