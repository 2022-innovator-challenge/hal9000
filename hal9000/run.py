# from timeit import default_timer
from typing import Any
from hal9000.github import (
    get_comments,
    get_issues,
)
from hal9000.nlp import run_nlp_on_list


def attach_comments(issues: list[dict[str, Any]], comments: list[dict[str, Any]]):
    for issue in issues:
        related_comments = [
            comment for comment in comments if comment["issue_url"] == issue["url"]
        ]
        if len(related_comments) != issue["comments"]:
            print(issue["number"], len(related_comments), issue["comments"])
        issue["comments"] = related_comments


# def print_time(step: str, since: float):
#     if args.verbose >= 1:
#         new_timer = default_timer()
#         print(step, new_timer - since, "seconds")
#         return new_timer
#     return since


def train(api_type: str, owner: str, repo: str):
    # time = default_timer()

    issues = [
        issue
        for issue in get_issues(api_type, owner, repo)
        if "pull_request" not in issue.keys()
    ]

    attach_comments(issues, get_comments(api_type, owner, repo))

    # time = print_time("Loaded", time)

    return run_nlp_on_list(issues)

    # time = print_time("NLP", time)

    # print_similarity(docs)

    # time = print_time("Similarity", time)

    # pprint(issues[0])
