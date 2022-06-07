import pathlib
from setuptools import setup
from setuptools import find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="aws-iam-generator",
    version="0.0.2",
    description="AWS IAM generator",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/jtyers/aws-iam-generator",
    author="Jonny Tyers",
    author_email="jonny@jonnytyers.co.uk",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=["aws-iam-utils"],
    entry_points={
        'console_scripts': [
            'aws-iam-generator = aws_iam_generator._internal.main:main',
        ]
    },
)
