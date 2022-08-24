from argparse import ArgumentParser

parser = ArgumentParser(description="Work in progress for Innovator Challenge 2022")
parser.add_argument("--verbose", "-v", dest="verbose", action="count", default=0)
parser.add_argument(
    "--issue",
    "-i",
    dest="issue",
    help="The issue number",
    required=True,
)
parser.add_argument(
    "--api",
    "-a",
    dest="api",
    help="Base URL of the GH API",
    choices=["COM", "WDF", "TOOLS"],
    default="COM",
)
parser.add_argument(
    "--owner",
    "-o",
    dest="owner",
    help="Repository owner",
    default="SAP",
)
parser.add_argument(
    "--repo",
    "-r",
    dest="repo",
    help="Repository name",
    default="cloud-sdk-js",
)

args = parser.parse_args()
