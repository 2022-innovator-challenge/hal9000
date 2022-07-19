from typing import Any
from datetime import datetime, timedelta
from collections import Counter


def get_last_commit_date(commit_list: list[Any]):
    try:
        return datetime.fromisoformat(commit_list[0]["author"]["date"].rstrip("Z"))
    except:
        return datetime.min


def print_results(results: list[Any]):
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
    for result in sorted(relevant, key=lambda r: r["repository"]["full_name"]):
        commit_counter = Counter([c["email"] for c in result["last_commit"][:100]])

        print(
            f"- [{result['repository']['full_name']}]({result['repository']['html_url']}) has {len(result['committers'])} committers ({', '.join([c[0] for c in commit_counter.most_common()[:4]])}), {len(result['last_commit'])} and uses {' & '.join(result['languages'].keys()[:3])}"
        )
    # print()
    # print("### Maintained projects")
    # for result in maintained:
    #     print(
    #         f"- [{result['repository']['full_name']}]({result['repository']['html_url']}) has {len(result['committers'])} committers"
    #     )
