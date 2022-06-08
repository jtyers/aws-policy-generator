import json

from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch

from aws_policy_generator._internal.main import main
from aws_iam_utils.checks import policies_are_equal
from aws_iam_utils.combiner import collapse_policy_statements
from aws_iam_utils.constants import LIST

from .testutil import dummy_policy
from .testutil import FULL_ACCESS
from .testutil import namespace

GENERATE_FROM_ARGS_ADDR = "aws_policy_generator._internal.main.generate_from_args"

def test_args_generate_single_list():
    expected_policy = dummy_policy()
    generate_from_args = Mock(side_effect=[ expected_policy ])

    with patch(GENERATE_FROM_ARGS_ADDR, new=generate_from_args) as m:
        result = main(['--list', 'iam'], return_policy=True)

    generate_from_args.assert_called_with(namespace(list=['iam']))

    assert policies_are_equal(json.loads(result), expected_policy)


def test_generate_single_read():
    expected_policy = dummy_policy()
    generate_from_args = Mock(side_effect=[ expected_policy ])

    with patch(GENERATE_FROM_ARGS_ADDR, new=generate_from_args) as m:
        result = main(['--read', 'iam'], return_policy=True)

    generate_from_args.assert_called_with(namespace(read=['iam']))

    assert policies_are_equal(json.loads(result), expected_policy)


def test_generate_single_write():
    expected_policy = dummy_policy()
    generate_from_args = Mock(side_effect=[ expected_policy ])

    with patch(GENERATE_FROM_ARGS_ADDR, new=generate_from_args) as m:
        result = main(['--write', 'iam'], return_policy=True)

    generate_from_args.assert_called_with(namespace(write=['iam']))

    assert policies_are_equal(json.loads(result), expected_policy)



def test_generate_single_full_access():
    expected_policy = dummy_policy()
    generate_from_args = Mock(side_effect=[ expected_policy ])

    with patch(GENERATE_FROM_ARGS_ADDR, new=generate_from_args) as m:
        result = main(['--full-access', 'iam'], return_policy=True)

    generate_from_args.assert_called_with(namespace(full_access=['iam']))

    assert policies_are_equal(json.loads(result), expected_policy)



def test_generate_multi():
    expected_policy = dummy_policy()
    generate_from_args = Mock(side_effect=[ expected_policy ])
    
    with patch(GENERATE_FROM_ARGS_ADDR, new=generate_from_args) as m:
        result = main([
            '--list', 'iam', 
            '--full-access', 's3', 
            '--full-access', 'ec2',
            '--read', 'lambda',
            '--read', 'cloudwatch',
        ], return_policy=True)

    generate_from_args.assert_called_with(namespace(
                list=['iam'], full_access=['s3', 'ec2'],
                read=['lambda', 'cloudwatch']))

    assert policies_are_equal(json.loads(result), expected_policy)

def test_generate_multi_with_actions():
    expected_policy = dummy_policy()
    generate_from_args = Mock(side_effect=[ expected_policy ])
    
    with patch(GENERATE_FROM_ARGS_ADDR, new=generate_from_args) as m:
        result = main([
            '--list', 'iam', 
            '--full-access', 's3',
            '--full-access', 'ec2',
            '--read', 'lambda',
            '--read', 'cloudwatch',
            '--action', 'ec2:DescribeInstances',
            '--action', 's3:ListAllMyBuckets',
        ], return_policy=True)

    generate_from_args.assert_called_with(namespace(
        list=['iam'], full_access=['s3', 'ec2'],
        read=['lambda', 'cloudwatch'],
        action=['ec2:DescribeInstances', 's3:ListAllMyBuckets']
    ))

    assert policies_are_equal(json.loads(result), expected_policy)
