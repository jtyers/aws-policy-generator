# aws-policy-generator

aws-policy-generator is a utility that allows for simple generation of IAM policies.

## Features

aws-policy-generator allows you to generate list-only, read-only, read-write or full-access policies for any AWS service via the command-line or a YAML config file.

I wrote it for those instances where you want a simple, non-repetitive way of granting broad-brush permissions to IAM roles. Generally, this tool works best for granting access to roles used by human users, particularly in dev environments, and not application roles. For applications you should write specific least-privilege policies to ensure any compromise of the application does not threaten other AWS resources.

`aws-policy-generator` is powered by my [aws-iam-utils](https://github.com/jtyers/aws-iam-utils) library, which is a Swiss-army knife for IAM policy generation, analysis and manipulation. If you need a programmatic way of working with policies, I recommend you use the library directly.

## Installation

As easy as:

```
pip install aws-policy-generator
```

## Usage

There are two ways to use this tool: directly via CLI, or via a YAML file. You can freely combine both approaches but when starting out I recommend choosing one or the other.

### CLI usage

You can get full help by running `aws-policy-generator --help`. Here are some examples to get you started. All of the command-line flags below can be combined or repeated to get the results you need.

To generate a policy granting full access to some services, for example IAM and S3:
```shell
# you can use -a instead of --full-access
>>> aws-policy-generator --full-access iam --full-access s3
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Resource": "*",
      "Action": [
        "iam:*",
        "s3:*"
      ]
    }
  ]
}
```

To grant read-only access, use `--read`/`-r`, list-only access use `--list`/`-l` and write access is `--write`/`-w`. Granting write will also grant read and list, and granting read will also grant list.

When using `--list`, `--read` or `--write` you can scope the permissions granted to specific types of resources (or ARN types). For example, suppose you wanted to grant someone access to manipulate IAM instance profiles only, you would do:

```shell
# you can use -a instead of --full-access
>>> aws-policy-generator --full-access iam:instance-profile
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Resource": "*",
      "Action": [
        "iam:addroletoinstanceprofile",
        "iam:createinstanceprofile",
        "iam:deleteinstanceprofile",
        "iam:getinstanceprofile",
        "iam:listinstanceprofiletags",
        "iam:listinstanceprofiles",
        "iam:removerolefrominstanceprofile",
        "iam:taginstanceprofile",
        "iam:untaginstanceprofile"
      ]
    }
  ]
}
```

You can also add specific actions to a policy:

```shell
# you can use -A instead of --action
>>> aws-policy-generator --action s3:ListMyBuckets
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Resource": "*",
      "Action": [
        "s3:listmybuckets"
      ]
    }
  ]
}
```

Sometimes the policies generated will be quite long. Depending on the type of policy you're trying to create, you may hit the AWS [policy length limits](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_iam-quotas.html). To help mitigate this issue, `aws-policy-generator` has support for shortening policies.

```shell
>>> aws-policy-generator -w iam -r s3 -w ec2 -w lambda --auto-shorten
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Resource": "*",
      "Action": [
        "s3:listmybuckets"
      ]
    }
  ]
}
```

### YAML usage

Check out the [example YAML file](https://github.com/jtyers/aws-policy-generator/blob/main/examples/multiple-services.yaml).

# Licence

MIT
