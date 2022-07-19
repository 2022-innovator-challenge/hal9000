from pprint import pprint
from timeit import default_timer
import sys
import json
from datetime import datetime, timedelta
from typing import Any
from time import sleep
from hal9000.github import (
    committers,
    get_comments,
    get_issue,
    get_issues,
    languages,
    last_commit,
    search_code,
)
from hal9000.nlp import print_similarity, run_nlp


def attach_comments(issues: list[dict[str, Any]], comments: list[dict[str, Any]]):
    for issue in issues:
        related_comments = [
            comment for comment in comments if comment["issue_url"] == issue["url"]
        ]
        if len(related_comments) != issue["comments"]:
            print(issue["number"], len(related_comments), issue["comments"])
        issue["comments"] = related_comments


def print_time(step: str, since: float):
    if "-v" in sys.argv:
        new_timer = default_timer()
        print(step, new_timer - since, "seconds")
        return new_timer
    return since


def format_repo(repository: Any):
    sleep(1)
    owner = repository["owner"]["login"]
    repo = repository["name"]
    print(f"Loading data for {owner}/{repo}")
    return {
        "repository": repository,
        "last_commit": last_commit(owner, repo),
        "committers": committers(owner, repo),
        "languages": languages(owner, repo),
    }


def get_last_commit_date(commit_list: list[Any]):
    try:
        return datetime.fromisoformat(commit_list[0]["author"]["date"].rstrip("Z"))
    except:
        return datetime.min


def main():
    if str(sys.argv[1]) == "sdk":
        try:
            with open("code_search.json", "r", encoding="utf8") as search_file:
                results = json.load(search_file)
        except FileNotFoundError:
            results = search_code("sap-cloud-sdk")

        if "--save" in sys.argv:
            with open("code_search.json", "w") as search_file:
                json.dump(
                    [format_repo(result["repository"]) for result in results],
                    search_file,
                    indent=2,
                )
                print("Search results saved to file")

        print(f"There are {len(results)} results in the API results")
        keys: list[str] = []
        filtered: list[Any] = []
        for result in results:
            if result["repository"]["full_name"] not in keys:
                keys.append(result["repository"]["full_name"])
                filtered.append(result)
        print(f"There are {len(filtered)} unique results")
        active = [
            result
            for result in filtered
            if datetime.utcnow() - timedelta(days=14)
            < get_last_commit_date(result["last_commit"])
        ]
        relevant = [
            result
            for result in active
            if len(result["last_commit"]) > 5
            and (
                "JavaScript" in result["languages"]
                or "TypeScript" in result["languages"]
                or "CAP CDS" in result["languages"]
            )
        ]
        print(f"There are {len(relevant)} relevant repos")
        maintained = [
            result
            for result in filtered
            if datetime.utcnow() - timedelta(days=240)
            < get_last_commit_date(result["last_commit"])
            and result not in relevant
            and len(result["last_commit"]) > 5
        ]
        print(f"There are {len(maintained)} maintained repos")
        inactive = [
            result
            for result in filtered
            if result not in maintained and result not in relevant
        ]
        print(f"There are {len(inactive)} inactive repos")
        print()
        print("### Active projects")
        for result in relevant:
            print(
                f"- [{result['repository']['full_name']}]({result['repository']['html_url']}) has {len(result['committers'])} committers and uses {' & '.join(result['languages'].keys())}"
            )
        print()
        print("### Maintained projects")
        # for result in maintained:
        #     print(
        #         f"- [{result['repository']['full_name']}]({result['repository']['html_url']}) has {len(result['committers'])} committers"
        #     )
    else:
        time = default_timer()

        issues = [
            issue
            for issue in get_issues("SAP", "cloud-sdk-js")
            if "pull_request" not in issue.keys()
        ]
        base_issue = get_issue("SAP", "cloud-sdk-js", str(sys.argv[1]))

        attach_comments(issues + [base_issue], get_comments("SAP", "cloud-sdk-js"))

        time = print_time("Loaded", time)

        docs = run_nlp(base_issue, issues)

        time = print_time("NLP", time)

        print_similarity(docs)

        time = print_time("Similarity", time)

        pprint(issues[0])
