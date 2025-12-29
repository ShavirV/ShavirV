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
        stargazerCount
        forkCount
        isFork
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

for r in repos:
    stars += r["stargazerCount"]
    forks += r["forkCount"]
    if r["primaryLanguage"]:
        lang = r["primaryLanguage"]["name"]
        language_count[lang] = language_count.get(lang, 0) + 1

metrics = {
    "user": USER,
    "generated_at": datetime.utcnow().isoformat() + "Z",
    "followers": data["followers"]["totalCount"],
    "following": data["following"]["totalCount"],
    "repositories": data["repositories"]["totalCount"],
    "stars": stars,
    "forks": forks,
    "commits": data["contributionsCollection"]["totalCommitContributions"],
    "top_languages": dict(
        sorted(language_count.items(), key=lambda x: x[1], reverse=True)
    )
}

with open("metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)

print("metrics.json updated")
