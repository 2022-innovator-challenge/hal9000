import sys

from hal9000.nlp import print_similarity

if __name__ == "__main__":
    from hal9000.run import train
    from hal9000.nlp import run_nlp_on_issue
    from hal9000.arguments import args
    from hal9000.github import get_issue

    docs = train(args.api, args.owner, args.repo)
    bd = run_nlp_on_issue(get_issue(args.api, args.owner, args.repo, args.issue))
    sys.exit(print(print_similarity(bd, docs)))
