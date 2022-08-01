from timeit import default_timer
import sys
from typing import Any
from hal9000.github import (
    get_comments,
    get_issue,
    get_issues,
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


def main():
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

    # pprint(issues[0])
