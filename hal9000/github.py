import os
from time import sleep
from typing import Any
import requests

token = os.getenv("GITHUB_TOKEN")
BASE_URL = "https://api.github.com"


def get(url: str) -> Any:
    res = requests.get(url, headers={"Authorization": f"token {token}"})
    if res.links.get("next"):
        if int(res.headers.get("X-RateLimit-Remaining", "0")) < 5:
            print("Rate limit is getting close...")
            sleep(5)
        return res.json() + get(res.links.get("next", {}).get("url"))
    return res.json()


def get_issues(owner: str, repo: str):
    return get(f"{BASE_URL}/repos/{owner}/{repo}/issues?state=all")
