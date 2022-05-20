# import spacy

from hal9000.github import get_issues


def main():

    print(get_issues("SAP", "cloud-sdk-js"))
    # nlp = spacy.load("en_core_web_trf")
