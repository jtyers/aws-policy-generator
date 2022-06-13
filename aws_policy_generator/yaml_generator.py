#!/usr/bin/env python3

import yaml

from aws_policy_generator.mappings import ACCESS_LEVELS_MAPPINGS
from aws_iam_utils.generator import generate_policy_for_service
from aws_iam_utils.generator import generate_policy_for_service_arn_type
from aws_iam_utils.generator import generate_full_policy_for_service
from aws_iam_utils.combiner import collapse_policy_statements
from aws_iam_utils.simplifier import simplify_policy
from aws_iam_utils.util import create_policy
from aws_iam_utils.util import statement

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


def generate_from_yaml(
    yamlInput, minimize=False, compact=False, auto_shorten=False, max_length=6144
):
    yamlData = yaml.safe_load(yamlInput)

    policies = []  # list of policies that we'll collapse together at the end

    for yamlDataPolicy in yamlData["policies"]:
        if "action" in yamlDataPolicy:
            action_name = yamlDataPolicy["action"]
            resource = yamlDataPolicy.get("resource", "*")
            policies.append(
                create_policy(statement(actions=action_name, resource=resource))
            )

        elif "service" in yamlDataPolicy:
            service_names = []
            if type(yamlDataPolicy["service"]) is list:
                service_names = yamlDataPolicy["service"]
            else:
                service_names = [yamlDataPolicy["service"]]

            for service_name in service_names:
                resource_types = yamlDataPolicy.get("resource_type", ["*"])
                access_level = yamlDataPolicy.get("access_level", "read")

                if ":" in service_name:
                    raise ValueError(
                        'service name cannot include ":", use resource_type to specify'
                        + " a resource type"
                    )

                if type(resource_types) is str:
                    resource_types = [resource_types]

                # attempt to map access_level
                access_levels = ACCESS_LEVELS_MAPPINGS[access_level]

                for resource_type in resource_types:
                    if resource_type == "*":
                        if access_level == "all":
                            policies.append(
                                generate_full_policy_for_service(service_name)
                            )
                        else:
                            policies.append(
                                generate_policy_for_service(service_name, access_levels)
                            )

                    else:
                        policies.append(
                            generate_policy_for_service_arn_type(
                                service_name, resource_type, access_levels
                            )
                        )

        else:
            raise ValueError(
                f'invalid input: {yamlDataPolicy}, must have "service" or "action" key'
            )

    policy = simplify_policy(collapse_policy_statements(*policies))

    return policy
