import os
from typing import Any
from flask import Flask
from hal9000.github import get_issue, post_comment
from hal9000.nlp import print_similarity, run_nlp_on_issue
from hal9000.run import train
from hal9000.webhooks import Webhook

app = Flask(__name__)
webhook = Webhook(app, secret=os.getenv("GITHUB_SECRET"))
docs = train("COM", "SAP", "cloud-sdk-js")


def get_api_type(url: str):
    if url.startswith("https://github.wdf.sap.corp"):
        return "WDF"
    if url.startswith("https://github.tools.sap"):
        return "TOOLS"
    return "COM"


@app.route("/")
def hello_world():
    return "<p>Hello, Flori!</p>"


@webhook.hook(event_type="issue_comment")
def on_issue_comment(data: Any):
    print("Received issue comment")

    if data["action"] == "created" and data["comment"]["body"] == "!similar":
        issue = get_issue(
            get_api_type(data["repository"]["url"]),
            data["repository"]["owner"]["login"],
            data["repository"]["name"],
            data["issue"]["number"],
        )
        issue["comments"] = []
        bd = run_nlp_on_issue(issue)
        post_comment(
            get_api_type(data["repository"]["url"]),
            data["repository"]["owner"]["login"],
            data["repository"]["name"],
            data["issue"]["number"],
            print_similarity(bd, docs),
        )


@webhook.hook(event_type="ping")
def on_ping():
    print("Received Ping!")
