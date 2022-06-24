import os
import json
from time import sleep
from typing import Any
import requests

token = os.getenv("GITHUB_TOKEN")
BASE_URL = "https://api.github.com"


def get(url: str) -> Any:
    if url == "":
        print("Called with empty URL. Something bad happened!")
        return []

    print("Getting issues...")
    res = requests.get(url, headers={"Authorization": f"token {token}"})
    if res.links.get("next"):
        if int(res.headers.get("X-RateLimit-Remaining", "0")) < 5:
            print("Rate limit is getting close...")
            sleep(5)
        return res.json() + get(res.links.get("next", {}).get("url", ""))
    return res.json()


def get_issues(owner: str, repo: str):
    try:
        with open("issues.json", "r") as issue_file:
            issues = json.load(issue_file)
            if len(issues):
                print("Issues loaded from file")
                print(len(issues))
                # TODO load new items from API
                return issues
    except:
        print("Error opening `issues.json`. File not present?")

    issues = get(f"{BASE_URL}/repos/{owner}/{repo}/issues?state=all")
    print("Issues loaded from API")

    with open("issues.json", "w") as issue_file:
        json.dump(issues, issue_file)
        print("Issues saved to file")

    print(len(issues))
    return issues
