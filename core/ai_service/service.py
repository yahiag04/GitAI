import os
import json
import ssl
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from typing import Optional, Literal, Any

import certifi

# Create SSL context with certifi certificates
_ssl_context = ssl.create_default_context(cafile=certifi.where())


COMMAND_PARSER_PROMPT = """You are a Git command interpreter. Parse the user's natural language input into a structured Git command.

Available actions:
- commit_changes: Save changes locally (optional: message)
- smart_commit: Commit with AI-generated message
- push_changes: Upload to remote repository
- pull_changes: Download latest from remote
- create_branch: Create a new branch (required: branch_name)
- checkout_branch: Switch to a branch (required: branch_name)
- delete_branch: Delete a branch (required: branch_name) [DANGEROUS]
- merge_branch: Merge branches (required: source_branch, optional: target_branch)
- stash_changes: Save changes temporarily
- stash_pop: Restore stashed changes
- stash_list: Show all stashes
- show_status: Show repository status
- show_diff: Show what changed
- init_repo: Initialize a new repository
- clone_repo: Clone a repository (required: clone_url)
- create_repository: Create GitHub repo (required: repository_name, optional: visibility)
- open_pull_request: Create PR (required: source_branch, target_branch)
- force_push: Force push [DANGEROUS]

Respond with ONLY valid JSON in this exact format:
{{
  "action": "action_name",
  "branch_name": "name if applicable",
  "source_branch": "source if applicable",
  "target_branch": "target if applicable",
  "message": "commit message if applicable",
  "clone_url": "url if applicable",
  "repository_name": "repo name if applicable",
  "visibility": "public or private if applicable",
  "requires_confirmation": true/false (true for dangerous actions),
  "reasoning": "brief explanation"
}}

If the input is not a Git command, return:
{{"action": null, "reasoning": "explanation of why it's not a git command"}}

User input: {input}

JSON response:"""


COMMIT_MESSAGE_PROMPT = """Analyze the following git diff and generate a concise, meaningful commit message.

Rules:
1. Start with a verb in imperative mood (Add, Fix, Update, Remove, Refactor, etc.)
2. Keep the first line under 50 characters
3. Be specific about what changed
4. Don't include file names unless necessary
5. Return ONLY the commit message, nothing else

Git diff:
```
{diff}
```

Commit message:"""


@dataclass
class AIService:
    """AI service for generating commit messages and other AI features."""

    provider: Literal["openai", "anthropic", "none"] = "none"
    api_key: Optional[str] = field(default=None, repr=False)
    model: str = ""

    def __post_init__(self) -> None:
        # Try to detect available API keys
        if self.api_key is None:
            openai_key = os.environ.get("OPENAI_API_KEY")
            anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

            if anthropic_key:
                self.provider = "anthropic"
                self.api_key = anthropic_key
                self.model = "claude-3-haiku-20240307"
            elif openai_key:
                self.provider = "openai"
                self.api_key = openai_key
                self.model = "gpt-4o-mini"
            else:
                self.provider = "none"

    def is_available(self) -> bool:
        """Check if AI service is configured."""
        return self.provider != "none" and self.api_key is not None

    def parse_command(self, user_input: str) -> Optional[dict]:
        """Parse natural language input into a structured command using AI."""
        if not self.is_available():
            return None

        prompt = COMMAND_PARSER_PROMPT.format(input=user_input)

        try:
            if self.provider == "anthropic":
                response = self._call_anthropic(prompt)
            elif self.provider == "openai":
                response = self._call_openai(prompt)
            else:
                return None

            # Clean up response - remove markdown code blocks if present
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            response = response.strip()

            # Parse JSON
            result = json.loads(response)
            return result

        except (json.JSONDecodeError, Exception):
            return None

    def generate_commit_message(self, diff: str) -> str:
        """Generate a commit message from a git diff."""
        if not self.is_available():
            return self._fallback_commit_message(diff)

        # Truncate diff if too long
        if len(diff) > 4000:
            diff = diff[:4000] + "\n... (truncated)"

        prompt = COMMIT_MESSAGE_PROMPT.format(diff=diff)

        try:
            if self.provider == "anthropic":
                return self._call_anthropic(prompt)
            elif self.provider == "openai":
                return self._call_openai(prompt)
        except Exception as e:
            return self._fallback_commit_message(diff)

        return self._fallback_commit_message(diff)

    def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic API."""
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        }
        data = {
            "model": self.model,
            "max_tokens": 100,
            "messages": [{"role": "user", "content": prompt}],
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=30, context=_ssl_context) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result["content"][0]["text"].strip()

    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API."""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        data = {
            "model": self.model,
            "max_tokens": 100,
            "messages": [{"role": "user", "content": prompt}],
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=30, context=_ssl_context) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"].strip()

    def _fallback_commit_message(self, diff: str) -> str:
        """Generate a basic commit message without AI."""
        lines = diff.split("\n")

        # Count changes
        additions = sum(1 for l in lines if l.startswith("+") and not l.startswith("+++"))
        deletions = sum(1 for l in lines if l.startswith("-") and not l.startswith("---"))

        # Extract file names
        files = []
        for line in lines:
            if line.startswith("+++ b/") or line.startswith("--- a/"):
                fname = line.split("/", 1)[-1] if "/" in line else line[6:]
                if fname and fname not in files and fname != "/dev/null":
                    files.append(fname)
            elif line.startswith("New file:"):
                fname = line.replace("New file:", "").strip()
                if fname not in files:
                    files.append(fname)

        # Generate message
        if not files:
            return "Update files"

        if len(files) == 1:
            action = "Add" if additions > deletions else "Update"
            return f"{action} {files[0]}"
        else:
            action = "Add" if additions > deletions * 2 else "Update"
            return f"{action} {len(files)} files"


def create_ai_service() -> AIService:
    """Create an AI service instance."""
    return AIService()
