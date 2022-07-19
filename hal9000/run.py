from pprint import pprint
from timeit import default_timer
import sys
import json
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
from hal9000.sdk import print_results


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


def format_repo(repository: Any) -> dict[str, Any]:
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


def main():
    if str(sys.argv[1]) == "sdk":
        try:
            with open("code_search.json", "r", encoding="utf8") as search_file:
                results = json.load(search_file)
        except FileNotFoundError:
            results = [
                format_repo(result["repository"])
                for result in search_code("sap-cloud-sdk filename=package.json")
            ]

        if "--save" in sys.argv:
            with open("code_search.json", "w") as search_file:
                json.dump(
                    results,
                    search_file,
                    indent=2,
                )
                if "-v" in sys.argv:
                    print("Search results saved to file")
        print_results(results)
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
