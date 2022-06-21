from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch
from io import StringIO

from aws_policy_generator import yaml_generator
from aws_iam_utils.constants import READ, WRITE, LIST
from aws_iam_utils.checks import policies_are_equal
from aws_iam_utils.combiner import collapse_policy_statements
from aws_iam_utils.util import create_policy
from aws_iam_utils.util import statement

from .testutil import dummy_policy
from .testutil import dummy_policy_arn_type
from .testutil import FULL_ACCESS

GENERATE_POLICY_FOR_SERVICE_ARN_TYPE_ADDR = (
    "aws_policy_generator.yaml_generator.generate_policy_for_service_arn_type"
)
GENERATE_POLICY_FOR_SERVICE_ADDR = (
    "aws_policy_generator.yaml_generator.generate_policy_for_service"
)
GENERATE_FULL_POLICY_FOR_SERVICE_ADDR = (
    "aws_policy_generator.yaml_generator.generate_full_policy_for_service"
)


def test_generate_single_list():
    input = """
    policies:
        - service: iam
          access_level: list
    """
    generate_policy_for_service = Mock(side_effect=dummy_policy)

    with patch(GENERATE_POLICY_FOR_SERVICE_ADDR, new=generate_policy_for_service):
        with StringIO(input) as y:
            result = yaml_generator.generate_from_yaml(y)

    generate_policy_for_service.assert_called_with("iam", [LIST])

    expected_policy = collapse_policy_statements(
        dummy_policy("iam", [LIST]),
    )
    assert policies_are_equal(result, expected_policy)


def test_generate_single_read():
    input = """
    policies:
        - service: iam
        # default access_level is read
    """
    generate_policy_for_service = Mock(side_effect=dummy_policy)

    with patch(GENERATE_POLICY_FOR_SERVICE_ADDR, new=generate_policy_for_service):
        with StringIO(input) as y:
            result = yaml_generator.generate_from_yaml(y)

    generate_policy_for_service.assert_called_with("iam", [LIST, READ])

    expected_policy = collapse_policy_statements(
        dummy_policy("iam", [LIST, READ]),
    )
    assert policies_are_equal(result, expected_policy)


def test_generate_single_write():
    input = """
    policies:
        - service: iam
          access_level: write
    """
    generate_policy_for_service = Mock(side_effect=dummy_policy)

    with patch(GENERATE_POLICY_FOR_SERVICE_ADDR, new=generate_policy_for_service):
        with StringIO(input) as y:
            result = yaml_generator.generate_from_yaml(y)

    generate_policy_for_service.assert_called_with("iam", [LIST, READ, WRITE])

    expected_policy = collapse_policy_statements(
        dummy_policy("iam", [LIST, READ, WRITE]),
    )
    assert policies_are_equal(result, expected_policy)


def test_generate_single_full_access():
    input = """
    policies:
        - service: iam
          access_level: all
    """
    generate_full_policy_for_service = Mock(side_effect=dummy_policy)

    with patch(
        GENERATE_FULL_POLICY_FOR_SERVICE_ADDR, new=generate_full_policy_for_service
    ):
        with StringIO(input) as y:
            result = yaml_generator.generate_from_yaml(y)

    generate_full_policy_for_service.assert_called_with("iam")

    expected_policy = collapse_policy_statements(
        dummy_policy("iam", [FULL_ACCESS]),
    )
    assert policies_are_equal(result, expected_policy)


def test_generate_multi():
    input = """
    policies:
        - service: iam
          access_level: list
        - service: ec2
          access_level: all
        - service: lambda
          access_level: read
        - service: cloudwatch
          access_level: read
        - service: s3
          access_level: all
    """

    generate_policy_for_service = Mock(side_effect=dummy_policy)
    generate_full_policy_for_service = Mock(side_effect=dummy_policy)
    with patch(GENERATE_POLICY_FOR_SERVICE_ADDR, new=generate_policy_for_service):
        with patch(
            GENERATE_FULL_POLICY_FOR_SERVICE_ADDR, new=generate_full_policy_for_service
        ):
            with StringIO(input) as y:
                result = yaml_generator.generate_from_yaml(y)

    generate_policy_for_service.assert_has_calls(
        [
            call("cloudwatch", [LIST, READ]),
            call("lambda", [LIST, READ]),
            call("iam", [LIST]),
        ],
        any_order=True,
    )
    generate_full_policy_for_service.assert_has_calls(
        [call("ec2"), call("s3")], any_order=True
    )

    expected_policy = collapse_policy_statements(
        dummy_policy("cloudwatch", [LIST, READ]),
        dummy_policy("lambda", [LIST, READ]),
        dummy_policy("iam", [LIST]),
        dummy_policy("s3", [FULL_ACCESS]),
        dummy_policy("ec2", [FULL_ACCESS]),
    )
    assert policies_are_equal(result, expected_policy)


def test_generate_multi_with_actions():
    input = """
    policies:
        - service: lambda
          access_level: read
        - service: cloudwatch
          access_level: read
        - action: ec2:DescribeInstances
        - action: s3:ListAllMyBuckets
        - action: wafv2:ListRules
    """

    generate_policy_for_service = Mock(side_effect=dummy_policy)
    with patch(GENERATE_POLICY_FOR_SERVICE_ADDR, new=generate_policy_for_service):
        with StringIO(input) as y:
            result = yaml_generator.generate_from_yaml(y)

    generate_policy_for_service.assert_has_calls(
        [
            call("cloudwatch", [LIST, READ]),
            call("lambda", [LIST, READ]),
        ],
        any_order=True,
    )

    expected_policy = collapse_policy_statements(
        dummy_policy("cloudwatch", [LIST, READ]),
        dummy_policy("lambda", [LIST, READ]),
        create_policy(
            statement(
                actions=["ec2:DescribeInstances", "s3:ListAllMyBuckets"], resource="*"
            )
        ),
        create_policy(statement(actions=["wafv2:ListRules"], resource="*")),
    )

    assert policies_are_equal(result, expected_policy)


def test_generate_with_action_and_resource():
    input = """
    policies:
        - action: wafv2:ListRules
          resource: arn:aws:wafv2:123456789012:eu-west-2:managed-rule/foo
    """

    generate_policy_for_service = Mock(side_effect=dummy_policy)
    with patch(GENERATE_POLICY_FOR_SERVICE_ADDR, new=generate_policy_for_service):
        with StringIO(input) as y:
            result = yaml_generator.generate_from_yaml(y)

    expected_policy = collapse_policy_statements(
        create_policy(
            statement(
                actions=["wafv2:ListRules"],
                resource="arn:aws:wafv2:123456789012:eu-west-2:managed-rule/foo",
            )
        ),
    )

    assert policies_are_equal(result, expected_policy)


def test_generate_with_action_and_multiple_resources():
    input = """
    policies:
        - action: wafv2:ListRules
          resource:
              - arn:aws:wafv2:123456789012:eu-west-2:managed-rule/foo
              - arn:aws:wafv2:123456789012:eu-west-2:managed-rule/bar
              - arn:aws:wafv2:123456789012:eu-west-2:managed-rule/baz
    """

    generate_policy_for_service = Mock(side_effect=dummy_policy)
    with patch(GENERATE_POLICY_FOR_SERVICE_ADDR, new=generate_policy_for_service):
        with StringIO(input) as y:
            result = yaml_generator.generate_from_yaml(y)

    expected_policy = collapse_policy_statements(
        create_policy(
            statement(
                actions=["wafv2:ListRules"],
                resource=[
                    "arn:aws:wafv2:123456789012:eu-west-2:managed-rule/foo",
                    "arn:aws:wafv2:123456789012:eu-west-2:managed-rule/bar",
                    "arn:aws:wafv2:123456789012:eu-west-2:managed-rule/baz",
                ],
            )
        ),
    )

    assert policies_are_equal(result, expected_policy)


def test_generate_multi_services():
    input = """
    policies:
        - access_level: read
          service:
          - lambda
          - cloudwatch
        - access_level: all
          service:
          - s3
    """

    generate_policy_for_service = Mock(side_effect=dummy_policy)
    generate_full_policy_for_service = Mock(side_effect=dummy_policy)

    with patch(GENERATE_POLICY_FOR_SERVICE_ADDR, new=generate_policy_for_service):
        with patch(
            GENERATE_FULL_POLICY_FOR_SERVICE_ADDR, new=generate_full_policy_for_service
        ):
            with StringIO(input) as y:
                result = yaml_generator.generate_from_yaml(y)

    generate_policy_for_service.assert_has_calls(
        [
            call("cloudwatch", [LIST, READ]),
            call("lambda", [LIST, READ]),
        ],
        any_order=True,
    )

    generate_full_policy_for_service.assert_has_calls([call("s3")], any_order=True)

    expected_policy = collapse_policy_statements(
        dummy_policy("cloudwatch", [LIST, READ]),
        dummy_policy("lambda", [LIST, READ]),
        dummy_policy("s3", [FULL_ACCESS]),
    )

    assert policies_are_equal(result, expected_policy)


def test_generate_multi_resource_types():
    input = """
    policies:
        - access_level: read
          service: lambda
          resource_type:
            - function
            - layer
    """

    generate_policy_for_service_arn_type = Mock(side_effect=dummy_policy_arn_type)

    with patch(
        GENERATE_POLICY_FOR_SERVICE_ARN_TYPE_ADDR,
        new=generate_policy_for_service_arn_type,
    ):
        with StringIO(input) as y:
            result = yaml_generator.generate_from_yaml(y)

    generate_policy_for_service_arn_type.assert_has_calls(
        [
            call("lambda", "function", [LIST, READ]),
            call("lambda", "layer", [LIST, READ]),
        ],
        any_order=True,
    )

    expected_policy = collapse_policy_statements(
        dummy_policy_arn_type("lambda", "function", [LIST, READ]),
        dummy_policy_arn_type("lambda", "layer", [LIST, READ]),
    )

    assert policies_are_equal(result, expected_policy)


def test_generate_no_input():
    input = """
    """

    with StringIO(input) as y:
        result = yaml_generator.generate_from_yaml(y)

    expected_policy = create_policy()
    assert policies_are_equal(result, expected_policy)
