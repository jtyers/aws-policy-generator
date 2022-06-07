import json
import sys

from aws_iam_generator import args_generator
from aws_iam_generator import yaml_generator
from aws_iam_generator._internal import argparser
from aws_iam_utils.combiner import collapse_policy_statements

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    args_namespace = argparser.parser.parse_args(args)

    policies = []

    if args_namespace.file:
        with open(args_namespace.file, 'r') as f:
            policies.append(yaml_generator.generate_from_yaml(f))

    policies.append(args_generator.generate_from_args(args_namespace))

    policy = collapse_policy_statements(*policies)

    if args_namespace.auto_shorten:
        policy_str = auto_shortener.auto_shorten_policy(policy, minimize=args_namespace.minimize, compact=args_namespace.compact, max_length=args_namespace.max_length)
    else:
        policy_str = json.dumps(policy, indent=2)

    print(policy_str)
