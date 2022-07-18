import os
import json
import sys
from pprint import pprint
from time import sleep
from typing import Any, Callable
import requests

# token = os.getenv("GITHUB_TOKEN")
token = os.getenv("GH_COM_TOKEN")
BASE_URL = "https://api.github.com"


def get_items(x: dict[str, Any]):
    return x["items"]


def identity(x: Any):
    return x


def get(
    url: str,
    accessor: Callable[[Any], Any] = identity,
    sleep_between_requests: int = 1,
    retry_counter: int = 0,
) -> Any:
    if url == "":
        print("Called with empty URL. Something bad happened!")
        return []

    if "-v" in sys.argv:
        print(f"Getting data from {url}")
    res = requests.get(url, headers={"Authorization": f"token {token}"})
    if res.status_code >= 400:
        if retry_counter < 3:
            print(f"Retrying after {sleep_between_requests * 10} seconds")
            sleep(sleep_between_requests * 10)
            return get(url, accessor, sleep_between_requests, retry_counter + 1)
        else:
            print(f"Getting data from {url} returned error code {res.status_code}")
            pprint(res.json())
    if res.links.get("next"):
        sleep(sleep_between_requests)
        if int(res.headers.get("X-RateLimit-Remaining", 0)) < 5:
            if "-v" in sys.argv:
                print("Rate limit is getting close...")
            sleep(5)
        return accessor(res.json()) + get(
            res.links.get("next", {}).get("url", ""), accessor, sleep_between_requests
        )
    return accessor(res.json())


def search_code(query: str):
    return get(f"{BASE_URL}/search/code?q={query}&per_page=100", get_items, 10)


def get_issue(owner: str, repo: str, number: str) -> dict[str, Any]:
    return get(f"{BASE_URL}/repos/{owner}/{repo}/issues/{number}")


def get_issues(owner: str, repo: str) -> list[dict[str, Any]]:
    try:
        with open("issues.json", "r", encoding="utf8") as issue_file:
            issues = json.load(issue_file)
            if len(issues):
                if "-v" in sys.argv:
                    print("Issues loaded from file")
                    print(len(issues))
                # TODO load new items from API
                return issues
    except FileNotFoundError:
        print("Error opening `issues.json`. File not present?")

    issues = get(f"{BASE_URL}/repos/{owner}/{repo}/issues?state=all&per_page=100")

    if "-v" in sys.argv:
        print("Issues loaded from API")

    with open("issues.json", "w", encoding="utf8") as issue_file:
        json.dump(issues, issue_file, indent=2)
        if "-v" in sys.argv:
            print("Issues saved to file")

    print(len(issues))
    return issues


def get_comments(owner: str, repo: str) -> list[dict[str, Any]]:
    try:
        with open("comments.json", "r", encoding="utf8") as issue_file:
            comments = json.load(issue_file)
            if len(comments):
                if "-v" in sys.argv:
                    print("Comments loaded from file")
                    print(len(comments))
                # TODO load new items from API
                return comments
    except FileNotFoundError:
        print("Error opening `comments.json`. File not present.")

    comments = get(
        f"{BASE_URL}/repos/{owner}/{repo}/issues/comments?state=all&per_page=100"
    )
    if "-v" in sys.argv:
        print("Comments loaded from API")
        print(len(comments))

    with open("comments.json", "w") as issue_file:
        json.dump(comments, issue_file, indent=2)
        if "-v" in sys.argv:
            print("Comments saved to file")

    return comments
