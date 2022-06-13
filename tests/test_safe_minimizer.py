from unittest.mock import Mock
from unittest.mock import patch

from aws_policy_generator.safe_minimizer import minimize_policy_with_error_handling
from aws_policy_generator.safe_minimizer import ACTION_NOT_FOUND_ERR

from aws_iam_utils.util import create_policy, statement, lowercase_policy
from aws_iam_utils.util import extract_policy_permission_items
from aws_iam_utils.checks import policies_are_equal

MINIMIZE_POLICY_ADDR = "aws_policy_generator.safe_minimizer.minimize_policy"


def create_failing_minimize_policy(failing_actions=[]):
    failing_actions_lower = [x.lower() for x in failing_actions]

    def failing_minimize_policy(p):
        ppi_actions = [x["action"] for x in extract_policy_permission_items(p)]

        for fa in failing_actions_lower:
            if fa in ppi_actions:
                raise Exception(f"{ACTION_NOT_FOUND_ERR} {fa}")

        return p

    return failing_minimize_policy


def test_minimize_policy_with_error_handling_happy_case():
    policy = create_policy(statement(actions=["s3:PutObject", "s3:GetObject"]))

    mp = Mock(side_effect=lambda x: x)

    with patch(MINIMIZE_POLICY_ADDR, new=mp):
        result = minimize_policy_with_error_handling(policy)

    mp.assert_called_with(lowercase_policy(policy))
    assert result == lowercase_policy(policy)


def test_minimize_policy_with_error_handling_error_in_one_statement():
    policy = create_policy(statement(actions=["s3:PutObject", "s3:GetObject"]))

    mp = Mock(side_effect=create_failing_minimize_policy(["s3:PutObject"]))

    with patch(MINIMIZE_POLICY_ADDR, new=mp):
        result = minimize_policy_with_error_handling(policy)

    assert policies_are_equal(result, lowercase_policy(policy))


def test_minimize_policy_with_error_handling_error_in_statement_with_qualifiers():
    policy = create_policy(
        statement(actions=["s3:GetObject"]),
        statement(actions=["s3:PutObject"], resource="foo", principal={"AWS": "bar"}),
    )

    mp = Mock(side_effect=create_failing_minimize_policy(["s3:PutObject"]))

    with patch(MINIMIZE_POLICY_ADDR, new=mp):
        result = minimize_policy_with_error_handling(policy)

    assert policies_are_equal(result, lowercase_policy(policy))


def test_minimize_policy_with_error_in_multiple_statement_with_qualifiers():
    policy = create_policy(
        statement(actions=["s3:GetObject"]),
        statement(actions=["s3:PutObject"], resource="foo", principal={"AWS": "bar"}),
        statement(
            actions=["s3:ListBucket"],
            resource="baz",
            condition={"StringEquals": {"bucketName": "bat"}},
        ),
        statement(actions=["s3:ListObject"], resource="bit"),
    )

    mp = Mock(
        side_effect=create_failing_minimize_policy(
            ["s3:PutObject", "s3:ListBucket", "s3:ListObject"]
        )
    )

    with patch(MINIMIZE_POLICY_ADDR, new=mp):
        result = minimize_policy_with_error_handling(policy)

    assert policies_are_equal(result, lowercase_policy(policy))
