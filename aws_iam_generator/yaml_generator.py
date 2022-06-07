#!/usr/bin/env python3

import argparse
import sys
import json
import yaml

from aws_iam_generator import mappings
from aws_iam_utils.generator import generate_policy_for_service
from aws_iam_utils.generator import generate_policy_for_service_arn_type
from aws_iam_utils.generator import generate_full_policy_for_service
from aws_iam_utils.constants import READ, WRITE, LIST, TAGGING, PERMISSIONS, ALL_ACCESS_LEVELS
from aws_iam_utils.combiner import collapse_policy_statements
from aws_iam_utils.simplifier import simplify_policy
from aws_iam_utils.util import create_policy
from aws_iam_utils.util import statement

from policyuniverse.expander_minimizer import minimize_policy

# YAML example:
#
# policies:
#   - service: iam
#     resource_type: policy
#     access_level: read
#   - service: s3
#     access_level: all
#   - action: ec2:DescribeRegions
#
# The access_level key can be list, read, write, tagging, permissions or all.


# auto-shorten: tuple of (minimize, compact)
AUTO_SHORTEN_ATTEMPT = [
    (False, False),
    (True, False),
    (True, True),
]

ACCESS_LEVELS_MAPPINGS = {
    'list': LIST,
    'read': READ,
    'write': WRITE,
    'tagging': TAGGING,
    'permissions': PERMISSIONS,
}

def generate_with_yaml(yamlInput, minimize=False, compact=False, auto_shorten=False, max_length=6144):
    yamlData = yaml.safe_load(yamlInput)

    policies = []  # list of policies that we'll collapse together at the end

    for yamlDataPolicy in yamlData['policies']:
        if 'action' in yamlDataPolicy:
            action_name = yamlDataPolicy['action']
            resource = yamlDataPolicy.get('resource', '*')
            policies.append(create_policy(statement(actions=action_name, resource=resource)))

        elif 'service' in yamlDataPolicy:
            service_name = yamlDataPolicy['service']
            resource_type = yamlDataPolicy.get('resource_type', '*')
            access_level = yamlDataPolicy.get('access_level', 'read')

            # attempt to map access_level
            access_levels = mappings.ACCESS_LEVELS_MAPPINGS[access_level]

            if resource_type == '*':
                if access_level == 'all':
                    policies.append(generate_full_policy_for_service(service_name))
                else:
                    policies.append(generate_policy_for_service(service_name, access_levels))

            else:
                policies.append(generate_policy_for_service_arn_type(service_name, resource_type, access_levels))

        else:
            raise ValueError(f'invalid input: {yamlDataPolicy}, must have "service" or "action" key')

    policy = json.dumps(simplify_policy(collapse_policy_statements(*policies)), indent=2)

    auto_shorten_attempts = AUTO_SHORTEN_ATTEMPT
    current_minimize = minimize
    current_compact = compact

    while True:
        if current_compact:
            policy = json.dumps(policy)
        
        if current_minimize:
            policy = json.dumps(minimize_policy(json.loads(policy)))

        policy_length = len(policy)
        if policy_length > max_length:
            if auto_shorten:
                if len(auto_shorten_attempts) == 0:
                    raise ValueError(f"The generated policy is {policy_length} characters, which is larger than the maximum {max_length} characters allowed. This policy is too long even after auto-shortening. Try specifying fewer arguments")

                current_minimize, current_compact = auto_shorten_attempts.pop(0)
                # loop again with new current_* args

            else:
                raise ValueError(f"The generated policy is {policy_length} characters, which is larger than the maximum {max_length} characters allowed. Try using --compact, --minimize, or specifying fewer arguments")

        else:
            break

    if policy_length > max_length:
        raise ValueError(f"The generated policy is {policy_length} characters, which is larger than the maximum {max_length} characters allowed. Try using --compact, --minimize, or specifying fewer arguments")

    return policy
