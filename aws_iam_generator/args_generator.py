#!/usr/bin/env python3

import argparse
import sys
import json


from aws_iam_generator import mappings
from aws_iam_utils.generator import generate_policy_for_service
from aws_iam_utils.generator import generate_policy_for_service_arn_type
from aws_iam_utils.generator import generate_full_policy_for_service
from aws_iam_utils.constants import READ, WRITE, LIST, ALL_ACCESS_LEVELS
from aws_iam_utils.combiner import collapse_policy_statements
from aws_iam_utils.simplifier import simplify_policy
from aws_iam_utils.util import create_policy
from aws_iam_utils.util import statement

from policyuniverse.expander_minimizer import minimize_policy

# auto-shorten: tuple of (minimize, compact)
AUTO_SHORTEN_ATTEMPT = [
    (False, False),
    (True, False),
    (True, True),
]

parser = argparse.ArgumentParser(
    description="Generate IAM policies from the command line"
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

def generate_from_args(args=sys.argv):
    # split into its own function to allow for unit testing
    args = parser.parse_args(args)

    policies = []  # list of policies that we'll mcollapse together at the end

    for item in [
            {
                'args': args.list,
                'access_levels': mappings.ACCESS_LEVELS_MAPPINGS['list'],
            },
            {
                'args': args.read,
                'access_levels': mappings.ACCESS_LEVELS_MAPPINGS['read'],
            },
            {
                'args': args.write,
                'access_levels': mappings.ACCESS_LEVELS_MAPPINGS['write'],
            },
            {
                'args': args.full_access,
                'access_levels': mappings.ACCESS_LEVELS_MAPPINGS['all'],
                'service_generator': generate_full_policy_for_service,
            },
        ]:

        if item['args']:
            for arg in item['args']:
                service_name = arg
                resource_type = '*'

                if ':' in arg:
                    service_name, resource_type = arg.split(':')

                if resource_type == '*':
                    if 'service_generator' in item:
                        policies.append(item['service_generator'](service_name))
                    else:
                        policies.append(generate_policy_for_service(service_name, item['access_levels']))
                else:
                    policies.append(generate_policy_for_service_arn_type(service_name, resource_type, item['access_levels']))

    if args.action:
        policies.append(create_policy(statement(actions=args.action, resource='*')))

    policy = json.dumps(simplify_policy(collapse_policy_statements(*policies)), indent=2)

    auto_shorten_attempts = AUTO_SHORTEN_ATTEMPT
    current_minimize = args.minimize
    current_compact = args.compact

    while True:
        if current_compact:
            policy = json.dumps(policy)
        
        if current_minimize:
            policy = json.dumps(minimize_policy(json.loads(policy)))

        policy_length = len(policy)
        if policy_length > args.max_length:
            if args.auto_shorten:
                if len(auto_shorten_attempts) == 0:
                    raise ValueError(f"The generated policy is {policy_length} characters, which is larger than the maximum {args.max_length} characters allowed. This policy is too long even after auto-shortening. Try specifying fewer arguments")

                current_minimize, current_compact = auto_shorten_attempts.pop(0)
                # loop again with new current_* args

            else:
                raise ValueError(f"The generated policy is {policy_length} characters, which is larger than the maximum {args.max_length} characters allowed. Try using --compact, --minimize, or specifying fewer arguments")

        else:
            break

    if policy_length > args.max_length:
        raise ValueError(f"The generated policy is {policy_length} characters, which is larger than the maximum {args.max_length} characters allowed. Try using --compact, --minimize, or specifying fewer arguments")

    return policy
