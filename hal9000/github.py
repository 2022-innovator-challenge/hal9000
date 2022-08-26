import os
import json

from pprint import pprint
from time import sleep
from typing import Any, Callable, TypedDict
from requests.auth import HTTPBasicAuth

import requests


class ApiInfo(TypedDict):
    api: str
    auth: HTTPBasicAuth
    verify: bool


API: dict[str, ApiInfo] = {
    "COM": {
        "api": "https://api.github.com",
        "auth": HTTPBasicAuth(os.getenv("GH_COM_USER"), os.getenv("GH_COM_TOKEN")),
        "verify": True,
    },
    "WDF": {
        "api": "https://github.wdf.sap.corp/api/v3",
        "auth": HTTPBasicAuth(os.getenv("GH_WDF_USER"), os.getenv("GH_WDF_TOKEN")),
        "verify": False,
    },
    "TOOLS": {
        "api": "https://github.tools.sap/api/v3",
        "auth": HTTPBasicAuth(os.getenv("GH_TOOLS_USER"), os.getenv("GH_TOOLS_TOKEN")),
        "verify": True,
    },
}


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
    api_type: str,
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

    res = requests.get(
        url,
        auth=API[api_type]["auth"],
        verify=API[api_type]["verify"],
    )
    if res.status_code >= 400:
        if retry_counter < 3:
            print(f"Retrying after {sleep_between_requests * 10} seconds")
            sleep(sleep_between_requests * 10)
            return get(
                api_type, url, accessor, sleep_between_requests, retry_counter + 1
            )
        print(f"Getting data from {url} returned error code {res.status_code}")
        pprint(res.json())
    if res.links.get("next") and load_next and next_counter < next_limit:
        sleep(sleep_between_requests)
        if int(res.headers.get("X-RateLimit-Remaining", 0)) < 5:
            print("Rate limit is getting close...")
            sleep(5)
        return accessor(res.json()) + get(
            api_type,
            res.links.get("next", {}).get("url", ""),
            accessor,
            sleep_between_requests,
            next_limit=next_limit,
            next_counter=next_counter + 1,
        )
    return accessor(res.json())


def post_comment(api_type: str, owner: str, repo: str, issue: str, body: str):
    print("Posting response")
    res = requests.post(
        f"{API[api_type]['api']}/repos/{owner}/{repo}/issues/{issue}/comments",
        auth=API[api_type]["auth"],
        verify=API[api_type]["verify"],
        data=json.dumps({"body": body}),
    )
    if not res.ok:
        print(res.status_code)
        print(res.json())
    return res


def last_commit(api_type: str, owner: str, repo: str) -> list[Any]:
    try:
        result = get(
            api_type,
            f"{API[api_type]['api']}/repos/{owner}/{repo}/commits?per_page=100",
            get_commit,
            next_limit=5,
        )
        # if args.verbose >= 2:
        #     pprint(result)
        return result
    except:
        return []


def search_code(api_type: str, query: str):
    return get(
        api_type,
        f"{API[api_type]['api']}/search/code?q={query}&per_page=100",
        get_items,
        10,
    )


def get_issue(api_type: str, owner: str, repo: str, number: str) -> dict[str, Any]:
    return get(api_type, f"{API[api_type]['api']}/repos/{owner}/{repo}/issues/{number}")


def get_issues(api_type: str, owner: str, repo: str) -> list[dict[str, Any]]:
    try:
        with open("issues.json", "r", encoding="utf8") as issue_file:
            issues = json.load(issue_file)
            if len(issues):
                # if args.verbose >= 1:
                #     print("Issues loaded from file")
                #     print(len(issues))
                # TODO load new items from API
                return issues
    except FileNotFoundError:
        print("Error opening `issues.json`. File not present?")

    issues = get(
        api_type,
        f"{API[api_type]['api']}/repos/{owner}/{repo}/issues?state=all&per_page=100",
    )

    # if args.verbose >= 1:
    #     print("Issues loaded from API")

    with open("issues.json", "w", encoding="utf8") as issue_file:
        json.dump(issues, issue_file, indent=2)
        # if args.verbose >= 1:
        #     print("Issues saved to file")

    print(len(issues))
    return issues


def get_comments(api_type: str, owner: str, repo: str) -> list[dict[str, Any]]:
    try:
        with open("comments.json", "r", encoding="utf8") as issue_file:
            comments = json.load(issue_file)
            if len(comments):
                # if args.verbose >= 1:
                #     print("Comments loaded from file")
                #     print(len(comments))
                # TODO load new items from API
                return comments
    except FileNotFoundError:
        print("Error opening `comments.json`. File not present.")

    comments = get(
        api_type,
        f"{API[api_type]['api']}/repos/{owner}/{repo}/issues/comments?state=all&per_page=100",
    )
    # if args.verbose >= 1:
    #     print("Comments loaded from API")
    #     print(len(comments))

    with open("comments.json", "w", encoding="utf8") as issue_file:
        json.dump(comments, issue_file, indent=2)
        # if args.verbose >= 1:
        #     print("Comments saved to file")

    return comments
