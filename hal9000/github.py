import os
import json
import sys
from pprint import pprint
from time import sleep
from typing import Any, Callable
import requests
from requests.auth import HTTPBasicAuth

BASE_WDF = "https://github.wdf.sap.corp/api/v3"
BASE_TOOLS = "https://github.tools.sap/api/v3"
BASE_COM = "https://api.github.com"
AUTH_WDF = HTTPBasicAuth(os.getenv("GH_WDF_USER"), os.getenv("GH_WDF_TOKEN"))
AUTH_TOOLS = HTTPBasicAuth(os.getenv("GH_TOOLS_USER"), os.getenv("GH_TOOLS_TOKEN"))
AUTH_COM = HTTPBasicAuth(os.getenv("GH_COM_USER"), os.getenv("GH_COM_TOKEN"))

API = BASE_COM
AUTH = AUTH_COM
VERIFY = True


def get_items(res: dict[str, Any]):
    return res["items"]


def get_login(contributors: list[dict[str, Any]]):
    return [contributor["login"] for contributor in contributors]


def get_commit(commits: list[dict[str, Any]]):
    return [
        {
            "author": c["commit"]["author"]["name"],
            "email": c["commit"]["author"]["email"],
            "date": c["commit"]["author"]["date"],
            "message": c["commit"]["message"],
        }
        for c in commits
    ]


def identity(res: Any):
    return res


def get(
    url: str,
    accessor: Callable[[Any], Any] = identity,
    sleep_between_requests: int = 1,
    retry_counter: int = 0,
    next_counter: int = 0,
    next_limit: int = 100,
    load_next: bool = True,
) -> Any:
    if url == "":
        print("Called with empty URL. Something bad happened!")
        return []

    if "-v" in sys.argv:
        print(f"Getting data from {url}")
    # res = requests.get(url, headers={"Authorization": f"token {token}"}, verify=False)
    res = requests.get(url, auth=AUTH, verify=VERIFY)
    if res.status_code >= 400:
        if retry_counter < 3:
            print(f"Retrying after {sleep_between_requests * 10} seconds")
            sleep(sleep_between_requests * 10)
            return get(url, accessor, sleep_between_requests, retry_counter + 1)
        print(f"Getting data from {url} returned error code {res.status_code}")
        pprint(res.json())
    if res.links.get("next") and load_next and next_counter < next_limit:
        sleep(sleep_between_requests)
        if int(res.headers.get("X-RateLimit-Remaining", 0)) < 5:
            if "-v" in sys.argv:
                print("Rate limit is getting close...")
            sleep(5)
        return accessor(res.json()) + get(
            res.links.get("next", {}).get("url", ""),
            accessor,
            sleep_between_requests,
            next_limit=next_limit,
            next_counter=next_counter + 1,
        )
    return accessor(res.json())


def last_commit(owner: str, repo: str) -> list[Any]:
    try:
        result = get(
            f"{API}/repos/{owner}/{repo}/commits?per_page=100", get_commit, next_limit=5
        )
        if "-vv" in sys.argv:
            pprint(result)
        return result
    except:
        return []


def search_code(query: str):
    return get(f"{API}/search/code?q={query}&per_page=100", get_items, 10)


def get_issue(owner: str, repo: str, number: str) -> dict[str, Any]:
    return get(f"{API}/repos/{owner}/{repo}/issues/{number}")


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

    issues = get(f"{API}/repos/{owner}/{repo}/issues?state=all&per_page=100")

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

    comments = get(f"{API}/repos/{owner}/{repo}/issues/comments?state=all&per_page=100")
    if "-v" in sys.argv:
        print("Comments loaded from API")
        print(len(comments))

    with open("comments.json", "w", encoding="utf8") as issue_file:
        json.dump(comments, issue_file, indent=2)
        if "-v" in sys.argv:
            print("Comments saved to file")

    return comments
