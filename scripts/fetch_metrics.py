"""
fetch_metrics.py

Fetch GitHub metrics for the README.
he 'validation' is just text to look cool. can you spot the bug causing the incorrect scramble? 
Metrics:
- Repository count
- Stars
- Forks
- GitHub contribution commits
- Followers
- Following
- Primary languages
- Total additions by ShavirV
- Total deletions by ShavirV

LOC is calculated using GitHub's contributor statistics endpoint rather
than querying individual commit histories. This gives a much more
representative lifetime contribution figure.

GitHub's contributor statistics endpoint can initially return HTTP 202
while GitHub calculates the statistics. The script automatically waits
and retries in that situation.
"""

import json
import os
import time
from datetime import datetime, timezone

import requests


# Configuration

USER = "ShavirV"
TOKEN = os.getenv("GITHUB_TOKEN")

if not TOKEN:
    raise RuntimeError("GITHUB_TOKEN not set")

GRAPHQL_URL = "https://api.github.com/graphql"
API_URL = "https://api.github.com"

# Current GitHub REST API version.
API_VERSION = "2026-03-10"

# Number of times to retry repository statistics when GitHub returns 202.
STATS_RETRIES = 10

# Initial delay after a 202 response.
STATS_RETRY_DELAY = 3

# General HTTP retries.
HTTP_RETRIES = 3


# HTTP session

session = requests.Session()

session.headers.update(
    {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
    }
)


# GraphQL helper

def graphql(query, variables=None):
    """Execute a GitHub GraphQL query with retries."""

    for attempt in range(HTTP_RETRIES):
        try:
            response = session.post(
                GRAPHQL_URL,
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

            # Retry transient GitHub errors.
            if response.status_code in (502, 503, 504):
                if attempt < HTTP_RETRIES - 1:
                    delay = 2 ** attempt
                    print(
                        f"Transient GitHub error "
                        f"{response.status_code}; "
                        f"retrying in {delay}s..."
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
            if attempt < HTTP_RETRIES - 1:
                delay = 2 ** attempt
                print(
                    f"GraphQL request failed: {exc}; "
                    f"retrying in {delay}s..."
                )
                time.sleep(delay)
                continue

            raise

    raise RuntimeError("GraphQL request failed after retries")


# Fetch user/repository metadata
#
# Deliberately does NOT fetch commit histories.

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
      first: 100
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


# Fetch contributor statistics

def get_contributor_stats(repo_name):
    """
    Fetch contributor statistics for one repository.

    Returns:
        (additions, deletions, commits)

    GitHub may return HTTP 202 while it calculates the statistics.
    In that case, wait and request the endpoint again.
    """

    url = (
        f"{API_URL}/repos/"
        f"{USER}/{repo_name}/stats/contributors"
    )

    for attempt in range(STATS_RETRIES):
        try:
            response = session.get(
                url,
                timeout=30,
            )

            print(
                f"  {repo_name}: "
                f"HTTP {response.status_code}, "
                f"remaining="
                f"{response.headers.get('X-RateLimit-Remaining')}"
            )

            # Statistics are being generated.
            if response.status_code == 202:
                if attempt == STATS_RETRIES - 1:
                    print(
                        f"  WARNING: GitHub did not finish generating "
                        f"statistics for {repo_name}"
                    )
                    return 0, 0, 0

                delay = STATS_RETRY_DELAY * (attempt + 1)

                print(
                    f"  Statistics are being generated; "
                    f"retrying in {delay}s..."
                )

                time.sleep(delay)
                continue

            # Empty repository.
            if response.status_code == 204:
                print(f"  {repo_name}: no contributor statistics")
                return 0, 0, 0

            # Repository contains 10,000+ commits.
            #
            # GitHub documents that contributor additions/deletions become
            # zero for repositories of this size.
            if response.status_code == 422:
                print(
                    f"  WARNING: {repo_name} has too many commits "
                    f"for contributor LOC statistics"
                )
                return 0, 0, 0

            # Retry transient server errors.
            if response.status_code in (500, 502, 503, 504):
                if attempt < HTTP_RETRIES - 1:
                    delay = 2 ** attempt

                    print(
                        f"  Transient error {response.status_code}; "
                        f"retrying in {delay}s..."
                    )

                    time.sleep(delay)
                    continue

            response.raise_for_status()

            contributors = response.json()

            # Find ShavirV in the contributor list.
            for contributor in contributors:
                author = contributor.get("author")

                if not author:
                    continue

                login = author.get("login")

                if login and login.lower() == USER.lower():
                    additions = 0
                    deletions = 0
                    commits = contributor.get("total", 0)

                    for week in contributor.get("weeks", []):
                        additions += week.get("a", 0)
                        deletions += week.get("d", 0)

                    print(
                        f"  {repo_name}: "
                        f"{commits:,} commits, "
                        f"+{additions:,} / -{deletions:,}"
                    )

                    return additions, deletions, commits

            # User did not appear as a contributor.
            print(f"  {repo_name}: no contributions found")
            return 0, 0, 0

        except requests.RequestException as exc:
            if attempt < HTTP_RETRIES - 1:
                delay = 2 ** attempt

                print(
                    f"  Request failed: {exc}; "
                    f"retrying in {delay}s..."
                )

                time.sleep(delay)
                continue

            print(
                f"  WARNING: failed to retrieve statistics "
                f"for {repo_name}: {exc}"
            )

            return 0, 0, 0

    return 0, 0, 0

# Process repositories

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

contributor_commits = 0


print()
print(f"Processing {len(repos)} repositories...")
print()


for repo in repos:
    repo_name = repo["name"]

    stars += repo["stargazerCount"]
    forks += repo["forkCount"]

    # Primary language

    language = repo.get("primaryLanguage")

    if language:
        language_name = language["name"]

        language_count[language_name] = (
            language_count.get(language_name, 0) + 1
        )

    # Contributor statistics

    additions, deletions, commits = get_contributor_stats(repo_name)

    loc_added += additions
    loc_removed += deletions
    contributor_commits += commits

# Build metrics

metrics = {
    "user": USER,
    "generated_at": datetime.now(timezone.utc).isoformat(),

    # Repository statistics
    "repos": user_data["repositories"]["totalCount"],
    "stars": stars,
    "forks": forks,

    # GitHub profile contribution count
    "commits": user_data["contributionsCollection"][
        "totalCommitContributions"
    ],

    # Lifetime contributor statistics across repositories
    "loc_added": loc_added,
    "loc_removed": loc_removed,

    # Profile
    "followers": user_data["followers"]["totalCount"],
    "following": user_data["following"]["totalCount"],

    # Languages
    "top_languages": dict(
        sorted(
            language_count.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    ),
}


# Write metrics.json

with open("metrics.json", "w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=2)

# Output summary

print()
print("=" * 50)
print("metrics.json updated")
print("=" * 50)
print(f"Repositories:       {metrics['repos']}")
print(f"Stars:              {metrics['stars']}")
print(f"Forks:              {metrics['forks']}")
print(f"GitHub commits:     {metrics['commits']}")
print(f"Contributor commits:{contributor_commits}")
print(f"LOC added:          {metrics['loc_added']:,}")
print(f"LOC removed:        {metrics['loc_removed']:,}")
print(f"Followers:          {metrics['followers']}")
print(f"Following:          {metrics['following']}")
print("=" * 50)
