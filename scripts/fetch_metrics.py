import json
import os
import time
from datetime import datetime, timezone

import requests

USER = "ShavirV"
TOKEN = os.getenv("GITHUB_TOKEN")

if not TOKEN:
    raise RuntimeError("GITHUB_TOKEN not set")

GRAPHQL_URL = "https://api.github.com/graphql"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "Content-Type": "application/json",
}

# Number of commits used for the LOC calculation per repository.
COMMITS_PER_REPO = 200

# Retry transient GitHub API failures.
MAX_RETRIES = 3


def graphql(query, variables=None):
    """Execute a GitHub GraphQL query with retries for transient failures."""

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                GRAPHQL_URL,
                headers=HEADERS,
                json={
                    "query": query,
                    "variables": variables or {},
                },
                timeout=30,
            )

            print(
                f"GraphQL: HTTP {response.status_code}, "
                f"remaining={response.headers.get('X-RateLimit-Remaining')}"
            )

            # GitHub occasionally returns transient 502/503/504 errors.
            if response.status_code in (502, 503, 504):
                if attempt < MAX_RETRIES - 1:
                    delay = 2 ** attempt
                    print(
                        f"Transient GitHub error "
                        f"{response.status_code}; retrying in {delay}s..."
                    )
                    time.sleep(delay)
                    continue

            response.raise_for_status()

            result = response.json()

            if "errors" in result:
                raise RuntimeError(
                    "GitHub GraphQL errors:\n"
                    + json.dumps(result["errors"], indent=2)
                )

            return result["data"]

        except requests.RequestException as exc:
            if attempt < MAX_RETRIES - 1:
                delay = 2 ** attempt
                print(
                    f"Request failed: {exc}; "
                    f"retrying in {delay}s..."
                )
                time.sleep(delay)
                continue

            raise

    raise RuntimeError("GitHub GraphQL request failed after retries")

USER_QUERY = """
query($user: String!) {
  user(login: $user) {
    followers {
      totalCount
    }

    following {
      totalCount
    }

    repositories(
      ownerAffiliations: OWNER
      first: 200
    ) {
      totalCount

      nodes {
        name
        isFork
        stargazerCount
        forkCount

        primaryLanguage {
          name
        }
      }
    }

    contributionsCollection {
      totalCommitContributions
    }
  }
}
"""

user_data = graphql(
    USER_QUERY,
    {"user": USER},
)["user"]


LOC_QUERY = """
query($owner: String!, $repo: String!, $first: Int!) {
  repository(owner: $owner, name: $repo) {
    defaultBranchRef {
      target {
        ... on Commit {
          history(first: $first) {
            nodes {
              additions
              deletions
            }
          }
        }
      }
    }
  }
}
"""


def get_repository_loc(repo_name):
    """Return additions and deletions for the latest commits of a repository."""

    data = graphql(
        LOC_QUERY,
        {
            "owner": USER,
            "repo": repo_name,
            "first": COMMITS_PER_REPO,
        },
    )

    repository = data.get("repository")

    if not repository:
        print(f"WARNING: Could not access repository {repo_name}")
        return 0, 0

    default_branch = repository.get("defaultBranchRef")

    if not default_branch:
        print(f"WARNING: Repository {repo_name} has no default branch")
        return 0, 0

    target = default_branch.get("target")

    if not target:
        print(f"WARNING: Repository {repo_name} has no commit target")
        return 0, 0

    history = target.get("history", {})
    commits = history.get("nodes", [])

    additions = 0
    deletions = 0

    for commit in commits:
        additions += commit.get("additions", 0)
        deletions += commit.get("deletions", 0)

    print(
        f"{repo_name}: "
        f"{len(commits)} commits, "
        f"+{additions:,} / -{deletions:,}"
    )

    return additions, deletions

repos = [
    repo
    for repo in user_data["repositories"]["nodes"]
    if not repo["isFork"]
]

language_count = {}
stars = 0
forks = 0
loc_added = 0
loc_removed = 0

for repo in repos:
    repo_name = repo["name"]

    stars += repo["stargazerCount"]
    forks += repo["forkCount"]

    language = repo.get("primaryLanguage")

    if language:
        language_name = language["name"]
        language_count[language_name] = (
            language_count.get(language_name, 0) + 1
        )

    # Fetch this repository's commit history separately.
    try:
        additions, deletions = get_repository_loc(repo_name)

        loc_added += additions
        loc_removed += deletions

    except Exception as exc:
        # Don't allow one problematic repository to prevent the entire
        # README from updating.
        print(
            f"WARNING: Failed to fetch LOC for {repo_name}: {exc}"
        )

metrics = {
    "user": USER,
    "generated_at": datetime.now(timezone.utc).isoformat(),

    "repos": user_data["repositories"]["totalCount"],
    "stars": stars,
    "forks": forks,
    "commits": user_data["contributionsCollection"][
        "totalCommitContributions"
    ],

    "loc_added": loc_added,
    "loc_removed": loc_removed,

    "followers": user_data["followers"]["totalCount"],
    "following": user_data["following"]["totalCount"],

    "top_languages": dict(
        sorted(
            language_count.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    ),
}


with open("metrics.json", "w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=2)


print()
print("metrics.json updated")
print(f"Repositories: {metrics['repos']}")
print(f"Stars:        {metrics['stars']}")
print(f"Forks:        {metrics['forks']}")
print(f"Commits:      {metrics['commits']}")
print(f"LOC added:    {metrics['loc_added']:,}")
print(f"LOC removed:  {metrics['loc_removed']:,}")
print(f"Followers:    {metrics['followers']}")
print(f"Following:    {metrics['following']}")
