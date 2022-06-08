#!/usr/bin/env python3

import sys
import json
import argparse


from aws_policy_generator._internal import argparser
from aws_policy_generator import mappings
from aws_policy_generator import auto_shortener
from aws_iam_utils.generator import generate_policy_for_service
from aws_iam_utils.generator import generate_policy_for_service_arn_type
from aws_iam_utils.generator import generate_full_policy_for_service
from aws_iam_utils.constants import READ, WRITE, LIST, ALL_ACCESS_LEVELS
from aws_iam_utils.combiner import collapse_policy_statements
from aws_iam_utils.simplifier import simplify_policy
from aws_iam_utils.util import create_policy
from aws_iam_utils.util import statement

from policyuniverse.expander_minimizer import minimize_policy

def generate_from_args(args_namespace):
    policies = []  # list of policies that we'll mcollapse together at the end

    for item in [
            {
                'args': args_namespace.list,
                'access_levels': mappings.ACCESS_LEVELS_MAPPINGS['list'],
            },
            {
                'args': args_namespace.read,
                'access_levels': mappings.ACCESS_LEVELS_MAPPINGS['read'],
            },
            {
                'args': args_namespace.write,
                'access_levels': mappings.ACCESS_LEVELS_MAPPINGS['write'],
            },
            {
                'args': args_namespace.full_access,
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

    if args_namespace.action:
        policies.append(create_policy(statement(actions=args_namespace.action, resource='*')))

    policy = simplify_policy(collapse_policy_statements(*policies))

    return policy
