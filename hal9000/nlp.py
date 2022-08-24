# from sense2vec import Sense2VecComponent
from typing import Any, Tuple
from spacy.tokens import Doc
from markdown import markdown
from bs4 import BeautifulSoup

import spacy

nlp = spacy.load("en_core_web_lg")


def get_plain_text(issue: dict[str, Any]):
    return BeautifulSoup(
        markdown(
            "\n\n".join(
                [
                    issue["title"],
                    issue["body"],
                    "\n\n".join(
                        [
                            comment.get("body", "")
                            for comment in issue.get("comments", [])
                        ]
                    ),
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


def run_nlp_on_issue(issue: dict[str, Any]):
    return (issue, nlp(get_plain_text(issue)))


def run_nlp_on_list(issues: list[Any]) -> Any:
    # s2v: Any = nlp.add_pipe("sense2vec")
    # s2v.from_disk("vectors/05_export2")

    return [run_nlp_on_issue(issue) for issue in issues]


def print_similarity(
    bd: Tuple[dict[str, Any], Doc], docs: list[Tuple[dict[str, Any], Doc]]
) -> str:
    base_issue, base_doc = bd

    top_3 = get_most_similar(docs, base_doc)[:3]
    intro = f"Most similar to {base_issue['title']} {base_issue['number']}"
    output = "\n".join(
        [
            f"  {index+1}. {result_issue['title']} #{result_issue['number']} - Score: {round(result_score, 3)}"
            for index, (result_issue, result_score) in enumerate(top_3)
        ]
    )

    print(intro, output)
    return intro + "\n" + output
