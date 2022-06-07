import argparse

parser = argparse.ArgumentParser(
    description="Generate IAM policies from the command line"
)
parser.add_argument(
    "-f",
    "--file",
    help="Specify a YAML file to process for policy generation",
)
parser.add_argument(
    "--max-length",
    type=int,
    default=6144,  # AWS max managed policy size
    help="Fail if policy length (in characters) exceeds this length.",
)
parser.add_argument(
    "--auto-shorten",
    action='store_true',
    default=False,
    help="Attempt to automatically shorten the policy if it's too long",
)
parser.add_argument(
    "-m",
    "--minimize",
    type=bool,
    default=False,
    help="Attempt to minimize policies",
)
parser.add_argument(
    "-c", "--compact",
    action="store_true",
    default=False,
    help="If specified, print compact JSON.",
)
parser.add_argument(
    "-A",
    "--action",
    action="append",
    help="Add a specific action to the policy",
)
parser.add_argument(
    "-a",
    "--full-access",
    action="append",
    help="Add full access for the specified services and resource type, which should be specified as service:type (e.g. ec2:instance) to the generated policy, can be repeated",
)
parser.add_argument(
    "-r",
    "--read",
    action="append",
    help="Add read access for the specified services and resource type, which should be specified as service:type (e.g. ec2:instance) to the generated policy, can be repeated",
)
parser.add_argument(
    "-w",
    "--write",
    action="append",
    help="Add write access for the specified services and resource type, which should be specified as service:type (e.g. ec2:instance) to the generated policy, can be repeated",
)
parser.add_argument(
    "-l",
    "--list",
    action="append",
    help="Add list access for the specified services and resource type, which should be specified as service:type (e.g. ec2:instance) to the generated policy, can be repeated",
)

