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


def __generate_yaml_action_item(item):
    action_name = item["action"]
    resource = item.get("resource", "*")
    return [create_policy(statement(actions=action_name, resource=resource))]


def __generate_yaml_service_item(item):
    result = []

    service_names = []
    if type(item["service"]) is list:
        service_names = item["service"]
    else:
        service_names = [item["service"]]

    for service_name in service_names:
        resource_types = item.get("resource_type", ["*"])
        access_level = item.get("access_level", "read")

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
                    result.append(generate_full_policy_for_service(service_name))
                else:
                    result.append(
                        generate_policy_for_service(service_name, access_levels)
                    )

            else:
                result.append(
                    generate_policy_for_service_arn_type(
                        service_name, resource_type, access_levels
                    )
                )

    return result


def generate_from_yaml(
    yamlInput, minimize=False, compact=False, auto_shorten=False, max_length=6144
):
    yamlData = yaml.safe_load(yamlInput)

    policies = []  # list of policies that we'll collapse together at the end

    if yamlData and yamlData.get("policies"):
        for yamlDataPolicy in yamlData["policies"]:
            if "action" in yamlDataPolicy:
                policies.extend(__generate_yaml_action_item(yamlDataPolicy))

            elif "service" in yamlDataPolicy:
                policies.extend(__generate_yaml_service_item(yamlDataPolicy))

            else:
                raise ValueError(
                    f'invalid input: {yamlDataPolicy}, must have "service" '
                    + ' or "action" key'
                )

    policy = simplify_policy(collapse_policy_statements(*policies))

    return policy
