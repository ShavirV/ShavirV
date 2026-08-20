import json
import os
from datetime import datetime, timezone

import requests

USER = "ShavirV"
TOKEN = os.getenv("GITHUB_TOKEN")

if not TOKEN:
    raise RuntimeError("GITHUB_TOKEN not set")

URL = "https://api.github.com/graphql"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "Content-Type": "application/json",
}


def graphql(query, variables=None):
    response = requests.post(
        URL,
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

    response.raise_for_status()

    result = response.json()

    if "errors" in result:
        raise RuntimeError(
            "GitHub GraphQL errors:\n"
            + json.dumps(result["errors"], indent=2)
        )

    return result["data"]


QUERY = """
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

data = graphql(
    QUERY,
    {"user": USER},
)["user"]


repos = [
    repo
    for repo in data["repositories"]["nodes"]
    if not repo["isFork"]
]


language_count = {}
stars = 0
forks = 0

for repo in repos:
    stars += repo["stargazerCount"]
    forks += repo["forkCount"]

    language = repo["primaryLanguage"]

    if language:
        name = language["name"]
        language_count[name] = language_count.get(name, 0) + 1


metrics = {
    "user": USER,
    "generated_at": datetime.now(timezone.utc).isoformat(),

    "repos": data["repositories"]["totalCount"],
    "stars": stars,
    "forks": forks,

    "commits": data["contributionsCollection"]["totalCommitContributions"],

    "loc_added": 0,
    "loc_removed": 0,

    "followers": data["followers"]["totalCount"],
    "following": data["following"]["totalCount"],

    "top_languages": dict(
        sorted(
            language_count.items(),
            key=lambda x: x[1],
            reverse=True,
        )
    ),
}


with open("metrics.json", "w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=2)


print("metrics.json updated")
