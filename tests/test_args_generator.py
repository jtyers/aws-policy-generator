import pytest
from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch
import json
import subprocess

from aws_iam_generator import args_generator
from aws_iam_utils.constants import READ, WRITE, LIST, ALL_ACCESS_LEVELS, TAGGING, PERMISSIONS
from aws_iam_utils.checks import policies_are_equal
from aws_iam_utils.combiner import collapse_policy_statements
from aws_iam_utils.util import create_policy
from aws_iam_utils.util import statement

FULL_ACCESS = "*"

GENERATE_POLICY_FOR_SERVICE_ADDR = 'aws_iam_generator.args_generator.generate_policy_for_service'
GENERATE_FULL_POLICY_FOR_SERVICE_ADDR = 'aws_iam_generator.args_generator.generate_full_policy_for_service'

def dummy_policy(service_name='svc', access_levels=[FULL_ACCESS]):
    return {
        'Version': '2012-10-17',
        'Statement': [
            {
                'Effect': 'Allow',
                'Action': [
                    f'{service_name.lower()}:{x.lower()}'
                    for x in access_levels
                ],
            }
        ]
    }


def test_generate_single_list():
    generate_policy_for_service = Mock(side_effect=dummy_policy)

    with patch(GENERATE_POLICY_FOR_SERVICE_ADDR, new=generate_policy_for_service) as m:
        result = args_generator.generate_from_args([ '-l', 'iam'])

    generate_policy_for_service.assert_called_with('iam', [LIST])

    expected_policy = collapse_policy_statements(
        dummy_policy('iam', [LIST]),
    )
    assert policies_are_equal(json.loads(result), expected_policy)


def test_generate_single_read():
    generate_policy_for_service = Mock(side_effect=dummy_policy)

    with patch(GENERATE_POLICY_FOR_SERVICE_ADDR, new=generate_policy_for_service) as m:
        result = args_generator.generate_from_args([ '-r', 'iam'])

    generate_policy_for_service.assert_called_with('iam', [LIST, READ])

    expected_policy = collapse_policy_statements(
        dummy_policy('iam', [LIST, READ]),
    )
    assert policies_are_equal(json.loads(result), expected_policy)


def test_generate_single_write():
    generate_policy_for_service = Mock(side_effect=dummy_policy)

    with patch(GENERATE_POLICY_FOR_SERVICE_ADDR, new=generate_policy_for_service) as m:
        result = args_generator.generate_from_args([ '-w', 'iam'])

    generate_policy_for_service.assert_called_with('iam', [LIST, READ, WRITE])

    expected_policy = collapse_policy_statements(
        dummy_policy('iam', [LIST, READ, WRITE]),
    )
    assert policies_are_equal(json.loads(result), expected_policy)


def test_generate_single_full_access():
    generate_full_policy_for_service = Mock(side_effect=dummy_policy)

    with patch(GENERATE_FULL_POLICY_FOR_SERVICE_ADDR, new=generate_full_policy_for_service) as m:
        result = args_generator.generate_from_args([ '-a', 'iam'])

    generate_full_policy_for_service.assert_called_with('iam')

    expected_policy = collapse_policy_statements(
        dummy_policy('iam', [FULL_ACCESS]),
    )
    assert policies_are_equal(json.loads(result), expected_policy)


def test_generate_multi():
    generate_policy_for_service = Mock(side_effect=dummy_policy)
    generate_full_policy_for_service = Mock(side_effect=dummy_policy)
    with patch(GENERATE_POLICY_FOR_SERVICE_ADDR, new=generate_policy_for_service):
        with patch(GENERATE_FULL_POLICY_FOR_SERVICE_ADDR, new=generate_full_policy_for_service):
            result = args_generator.generate_from_args([
                '-l', 'iam',
                '-a', 's3',
                '-r', 'lambda',
                '-r', 'cloudwatch',
                '-a', 'ec2',
            ])

    generate_policy_for_service.assert_has_calls([
        call('cloudwatch', [LIST, READ]),
        call('lambda', [LIST, READ]),
        call('iam', [LIST]),
    ], any_order=True)
    generate_full_policy_for_service.assert_has_calls([
        call('ec2'), call('s3')], any_order=True)

    expected_policy = collapse_policy_statements(
        dummy_policy('cloudwatch', [LIST, READ]),
        dummy_policy('lambda', [LIST, READ]),
        dummy_policy('iam', [LIST]),
        dummy_policy('s3', [FULL_ACCESS]),
        dummy_policy('ec2', [FULL_ACCESS]),
    )
    assert policies_are_equal(json.loads(result), expected_policy)

def test_generate_multi_with_actions():
    generate_policy_for_service = Mock(side_effect=dummy_policy)
    with patch(GENERATE_POLICY_FOR_SERVICE_ADDR, new=generate_policy_for_service):
        result = args_generator.generate_from_args([
            '-r', 'lambda',
            '-r', 'cloudwatch',
            '-A', 'ec2:DescribeInstances',
            '-A', 's3:ListAllMyBuckets',
            '-A', 'wafv2:ListRules',
        ])

    generate_policy_for_service.assert_has_calls([
        call('cloudwatch', [LIST, READ]),
        call('lambda', [LIST, READ]),
    ], any_order=True)

    expected_policy = collapse_policy_statements(
        dummy_policy('cloudwatch', [LIST, READ]),
        dummy_policy('lambda', [LIST, READ]),
        create_policy(
            statement(actions=['ec2:DescribeInstances','s3:ListAllMyBuckets'],resource='*')
        ),
        create_policy(
            statement(actions=['wafv2:ListRules'],resource='*')
        ),
    )

    assert policies_are_equal(json.loads(result), expected_policy)
