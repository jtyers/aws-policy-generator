import argparse
import sys

from aws_iam_generator import args_generator
from aws_iam_generator._internal import argparse

def main(args=None):
    if args is None:
        args = sys.argv[1:]


    print(args_generator.generate_from_args(args))
