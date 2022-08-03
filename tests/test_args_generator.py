from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch

from aws_policy_generator import args_generator
from aws_iam_utils.constants import (
    READ,
    WRITE,
    LIST,
)
from aws_iam_utils.checks import policies_are_equal
from aws_iam_utils.combiner import collapse_policy_statements
from aws_iam_utils.util import create_policy
from aws_iam_utils.util import statement

from .testutil import dummy_policy
from .testutil import dummy_policy_arn_type
from .testutil import FULL_ACCESS
from .testutil import namespace

GENERATE_POLICY_FOR_SERVICE_ADDR = (
    "aws_policy_generator.args_generator.generate_policy_for_service"
)
GENERATE_POLICY_FOR_SERVICE_ARN_TYPE_ADDR = (
    "aws_policy_generator.args_generator.generate_policy_for_service_arn_type"
)
GENERATE_FULL_POLICY_FOR_SERVICE_ADDR = (
    "aws_policy_generator.args_generator.generate_full_policy_for_service"
)


def test_generate_single_list():
    generate_policy_for_service = Mock(side_effect=dummy_policy)

    with patch(GENERATE_POLICY_FOR_SERVICE_ADDR, new=generate_policy_for_service):
        result = args_generator.generate_from_args(namespace(list=["iam"]))

    generate_policy_for_service.assert_called_with("iam", [LIST])

    expected_policy = collapse_policy_statements(
        dummy_policy("iam", [LIST]),
    )
    assert policies_are_equal(result, expected_policy)


def test_generate_single_read():
    generate_policy_for_service = Mock(side_effect=dummy_policy)

    with patch(GENERATE_POLICY_FOR_SERVICE_ADDR, new=generate_policy_for_service):
        result = args_generator.generate_from_args(namespace(read=["iam"]))

    generate_policy_for_service.assert_called_with("iam", [LIST, READ])

    expected_policy = collapse_policy_statements(
        dummy_policy("iam", [LIST, READ]),
    )
    assert policies_are_equal(result, expected_policy)


def test_generate_single_write():
    generate_policy_for_service = Mock(side_effect=dummy_policy)

    with patch(GENERATE_POLICY_FOR_SERVICE_ADDR, new=generate_policy_for_service):
        result = args_generator.generate_from_args(namespace(write=["iam"]))

    generate_policy_for_service.assert_called_with("iam", [LIST, READ, WRITE])

    expected_policy = collapse_policy_statements(
        dummy_policy("iam", [LIST, READ, WRITE]),
    )
    assert policies_are_equal(result, expected_policy)


def test_generate_single_full_access():
    generate_full_policy_for_service = Mock(side_effect=dummy_policy)

    with patch(
        GENERATE_FULL_POLICY_FOR_SERVICE_ADDR, new=generate_full_policy_for_service
    ):
        result = args_generator.generate_from_args(namespace(full_access=["iam"]))

    generate_full_policy_for_service.assert_called_with("iam")

    expected_policy = collapse_policy_statements(
        dummy_policy("iam", [FULL_ACCESS]),
    )
    assert policies_are_equal(result, expected_policy)


def test_generate_multi():
    generate_policy_for_service = Mock(side_effect=dummy_policy)
    generate_full_policy_for_service = Mock(side_effect=dummy_policy)
    with patch(GENERATE_POLICY_FOR_SERVICE_ADDR, new=generate_policy_for_service):
        with patch(
            GENERATE_FULL_POLICY_FOR_SERVICE_ADDR, new=generate_full_policy_for_service
        ):
            result = args_generator.generate_from_args(
                namespace(
                    list=["iam"],
                    full_access=["s3", "ec2"],
                    read=["lambda", "cloudwatch"],
                )
            )

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
    generate_policy_for_service = Mock(side_effect=dummy_policy)
    with patch(GENERATE_POLICY_FOR_SERVICE_ADDR, new=generate_policy_for_service):
        result = args_generator.generate_from_args(
            namespace(
                read=["lambda", "cloudwatch"],
                action=[
                    "ec2:DescribeInstances",
                    "s3:ListAllMyBuckets",
                    "wafv2:ListRules",
                ],
            )
        )

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


def test_generate_service_arn_type_with_wildcard_arns():
    generate_policy_for_service_arn_type = Mock(side_effect=dummy_policy_arn_type)
    with patch(
        GENERATE_POLICY_FOR_SERVICE_ARN_TYPE_ADDR,
        new=generate_policy_for_service_arn_type,
    ):
        result = args_generator.generate_from_args(
            namespace(
                read=["ssm:parameter", "ec2:vpc-flow-log"],
                include_service_wide_actions=True,
            )
        )

    generate_policy_for_service_arn_type.assert_has_calls(
        [
            call("ssm", "parameter", [LIST, READ], include_service_wide_actions=True),
            call(
                "ec2", "vpc-flow-log", [LIST, READ], include_service_wide_actions=True
            ),
        ],
        any_order=True,
    )

    expected_policy = collapse_policy_statements(
        dummy_policy_arn_type(
            "ssm", "parameter", [LIST, READ], include_service_wide_actions=True
        ),
        dummy_policy_arn_type(
            "ec2", "vpc-flow-log", [LIST, READ], include_service_wide_actions=True
        ),
    )

    assert policies_are_equal(result, expected_policy)


def test_generate_service_arn_type_without_wildcard_arns():
    generate_policy_for_service_arn_type = Mock(side_effect=dummy_policy_arn_type)
    with patch(
        GENERATE_POLICY_FOR_SERVICE_ARN_TYPE_ADDR,
        new=generate_policy_for_service_arn_type,
    ):
        result = args_generator.generate_from_args(
            namespace(
                read=["ssm:parameter", "ec2:vpc-flow-log"],
            )
        )

    generate_policy_for_service_arn_type.assert_has_calls(
        [
            call("ssm", "parameter", [LIST, READ], include_service_wide_actions=False),
            call(
                "ec2", "vpc-flow-log", [LIST, READ], include_service_wide_actions=False
            ),
        ],
        any_order=True,
    )

    expected_policy = collapse_policy_statements(
        dummy_policy_arn_type(
            "ssm", "parameter", [LIST, READ], include_service_wide_actions=False
        ),
        dummy_policy_arn_type(
            "ec2", "vpc-flow-log", [LIST, READ], include_service_wide_actions=False
        ),
    )

    assert policies_are_equal(result, expected_policy)
