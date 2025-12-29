import requests
import json
import os
from datetime import datetime

USER = "ShavirV"
TOKEN = os.getenv("GITHUB_TOKEN")

if not TOKEN:
    raise RuntimeError("GITHUB_TOKEN not set")

QUERY = """
query($user:String!) {
  user(login: $user) {
    followers { totalCount }
    following { totalCount }
    repositories(ownerAffiliations: OWNER, first: 100) {
      totalCount
      nodes {
        name
        isFork
        stargazerCount
        forkCount
        primaryLanguage {
          name
        }
        defaultBranchRef {
          target {
            ... on Commit {
              history(first: 100) {
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
    contributionsCollection {
      totalCommitContributions
    }
  }
}
"""

resp = requests.post(
    "https://api.github.com/graphql",
    headers={"Authorization": f"Bearer {TOKEN}"},
    json={"query": QUERY, "variables": {"user": USER}},
    timeout=20
)

resp.raise_for_status()
data = resp.json()["data"]["user"]

repos = [r for r in data["repositories"]["nodes"] if not r["isFork"]]

language_count = {}
stars = 0
forks = 0
loc_added = 0
loc_removed = 0

for r in repos:
    stars += r["stargazerCount"]
    forks += r["forkCount"]

    if r["primaryLanguage"]:
        lang = r["primaryLanguage"]["name"]
        language_count[lang] = language_count.get(lang, 0) + 1

    history = (
        r.get("defaultBranchRef", {})
         .get("target", {})
         .get("history", {})
         .get("nodes", [])
    )

    for commit in history:
        loc_added += commit.get("additions", 0)
        loc_removed += commit.get("deletions", 0)

metrics = {
    "user": USER,
    "generated_at": datetime.utcnow().isoformat() + "Z",

    # renamed keys for SVG generator
    "repos": data["repositories"]["totalCount"],
    "stars": stars,
    "forks": forks,
    "commits": data["contributionsCollection"]["totalCommitContributions"],
    "loc_added": loc_added,
    "loc_removed": loc_removed,

    # extra useful stats
    "followers": data["followers"]["totalCount"],
    "following": data["following"]["totalCount"],
    "top_languages": dict(
        sorted(language_count.items(), key=lambda x: x[1], reverse=True)
    )
}

with open("metrics.json", "w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=2)

print("metrics.json updated")
