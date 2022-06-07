import sys

from aws_iam_generator import args_generator
from aws_iam_generator._internal import argparser

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    args_namespace = argparser.parser.parse_args(args)
    print(args_generator.generate_from_args(args_namespace))
