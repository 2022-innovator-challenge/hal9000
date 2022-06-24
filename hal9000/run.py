# import spacy
from pprint import pprint
from hal9000.github import get_issues


def main():

    issues = get_issues("SAP", "cloud-sdk-js")

    issue = issues[1234]

    pprint(issue["title"])

    # nlp = spacy.load("en_core_web_trf")
