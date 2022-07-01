import spacy
from spacy.tokens import Doc
from typing import Any, Tuple
from markdown import markdown
from bs4 import BeautifulSoup


def get_plain_text(issue: dict[str, Any]):
    return BeautifulSoup(
        markdown(
            "\n\n".join(
                [
                    issue["title"],
                    issue["body"],
                    "\n\n".join([comment["body"] for comment in issue["comments"]]),
                ]
            )
        ),
        "html.parser",
    ).get_text()


def get_most_similar(docs: list[tuple[Any, Doc]], base_issue_doc: Doc):
    return sorted(
        ((other_issue, base_issue_doc.similarity(doc)) for other_issue, doc in docs),
        key=lambda x: x[1],
        reverse=True,
    )


def run_nlp(base_issue: dict[str, Any], issues: list[Any]) -> Any:
    nlp = spacy.load("en_core_web_lg")
    s2v: Any = nlp.add_pipe("sense2vec")
    s2v.from_disk("vectors/s2v_old")

    return [(issue, nlp(get_plain_text(issue))) for issue in [base_issue] + issues]


def print_similarity(docs: list[Tuple[dict[str, Any], Doc]]):
    base_issue, base_doc = docs.pop(0)

    top_10 = get_most_similar(docs, base_doc)[:10]
    print("Most similar to", base_issue["title"], base_issue["number"])
    for index, (result_issue, result_score) in enumerate(top_10):
        print(
            f"  {index+1}.",
            result_issue["title"],
            result_issue["number"],
            " - Score:",
            result_score,
        )
