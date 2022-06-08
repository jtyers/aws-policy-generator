import json

from aws_policy_generator._internal.main import main
from aws_iam_utils.checks import policies_are_equal
from aws_iam_utils.combiner import collapse_policy_statements
from aws_iam_utils.constants import LIST, READ, WRITE
from aws_iam_utils.generator import generate_full_policy_for_service
from aws_iam_utils.generator import generate_policy_for_service
from aws_iam_utils.generator import generate_policy_for_service_arn_type
from aws_iam_utils.util import create_policy
from aws_iam_utils.util import statement

def test_generate_example_yaml():
    result = main([ '-f', './examples/multiple-services.yaml'],
                  return_policy=True)

    expected_policy = collapse_policy_statements(
        generate_policy_for_service('iam', [ LIST ]),
        generate_policy_for_service_arn_type('ec2', 'instance', [ LIST, READ, WRITE ]),
        generate_policy_for_service('lambda', [ LIST, READ ]),
        generate_full_policy_for_service('s3'),
        generate_policy_for_service('lambda', [ LIST, READ ]),
        generate_policy_for_service('s3', [ LIST, READ ]),
        generate_policy_for_service('iam', [ LIST, READ ]),
        create_policy(
            statement(actions='s3:ListBucket', resource='arn:aws:s3:::my-test-bucket'),
            statement(actions='s3:ListBucket', resource=[
                'arn:aws:s3:::my-test-bucket',
                'arn:aws:s3:::my-test-bucket/*',
            ]),
        )
    )

    assert policies_are_equal(json.loads(result), expected_policy)

