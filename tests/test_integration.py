import json

from aws_policy_generator._internal.main import main
from aws_iam_utils.checks import policies_are_equal
from aws_iam_utils.combiner import collapse_policy_statements
from aws_iam_utils.constants import LIST, READ, WRITE, ALL_ACCESS_LEVELS
from aws_iam_utils.generator import generate_full_policy_for_service
from aws_iam_utils.generator import generate_policy_for_service
from aws_iam_utils.generator import generate_policy_for_service_arn_type
from aws_iam_utils.util import create_policy
from aws_iam_utils.util import statement


def test_generate_example_yaml():
    result = main("-f ./examples/multiple-services.yaml".split(" "), return_policy=True)

    expected_policy = collapse_policy_statements(
        generate_policy_for_service("iam", [LIST]),
        generate_policy_for_service_arn_type(
            "iam", "instance-profile", ALL_ACCESS_LEVELS
        ),
        generate_policy_for_service_arn_type("ec2", "instance", [LIST, READ, WRITE]),
        generate_policy_for_service("lambda", [LIST, READ]),
        generate_full_policy_for_service("s3"),
        generate_policy_for_service("lambda", [LIST, READ]),
        generate_policy_for_service("s3", [LIST, READ]),
        generate_policy_for_service("iam", [LIST, READ]),
        create_policy(
            statement(actions="s3:ListBucket", resource="arn:aws:s3:::my-test-bucket"),
            statement(
                actions="s3:ListBucket",
                resource=[
                    "arn:aws:s3:::my-test-bucket",
                    "arn:aws:s3:::my-test-bucket/*",
                ],
            ),
        ),
    )
    assert policies_are_equal(json.loads(result), expected_policy)


def test_generate_readme_args_iam_role_full_access():
    result = main("-a iam:role".split(" "), return_policy=True)

    expected_policy = collapse_policy_statements(
        generate_policy_for_service_arn_type("iam", "role", ALL_ACCESS_LEVELS),
    )
    assert policies_are_equal(json.loads(result), expected_policy)


def test_generate_readme_args_full_access_iam_s3():
    result = main("-a iam -a s3".split(" "), return_policy=True)

    expected_policy = collapse_policy_statements(
        generate_full_policy_for_service("iam"),
        generate_full_policy_for_service("s3"),
    )
    assert policies_are_equal(json.loads(result), expected_policy)


def test_generate_readme_args_list_iam_s3():
    result = main("-l iam -l s3".split(" "), return_policy=True)

    expected_policy = collapse_policy_statements(
        generate_policy_for_service("iam", [LIST]),
        generate_policy_for_service("s3", [LIST]),
    )
    assert policies_are_equal(json.loads(result), expected_policy)


def test_generate_readme_args_read_iam_s3():
    result = main("-r iam -r s3".split(" "), return_policy=True)

    expected_policy = collapse_policy_statements(
        generate_policy_for_service("iam", [LIST, READ]),
        generate_policy_for_service("s3", [LIST, READ]),
    )
    assert policies_are_equal(json.loads(result), expected_policy)


def test_generate_readme_args_write_iam_s3():
    result = main("-w iam -w s3".split(" "), return_policy=True)

    expected_policy = collapse_policy_statements(
        generate_policy_for_service("iam", [LIST, READ, WRITE]),
        generate_policy_for_service("s3", [LIST, READ, WRITE]),
    )
    assert policies_are_equal(json.loads(result), expected_policy)
