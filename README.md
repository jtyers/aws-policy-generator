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

(Note: please read the **Important: wildcard-ARN actions** section below.)
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

For more complex policies, or automated usage (for example, my clients often use this as part of an infrastructure-as-code pipeline), YAML is often better and, of course, can be committed to Git. Here's example YAML code to give you a flavour.

(Note: please read the **Important: wildcard-ARN actions** section below.)

```yaml
# aws-policy-generator uses a simple format for policy generation.
#
# Under the 'policies' key there can be either 'service' or 'action' items.
#
# See below for examples.

policies:
    # Adds permissions for all of the IAM service. Only list
    # permissions are granted, so read/write/tagging/permissions related
    # actions are excluded.
    - service: iam
      access_level: list

    # Adds permissions for the instance resource type in EC2.
    # Write, Read and List permissions are granted, but tagging/permissions
    # actions are excluded.
    - service: ec2
      access_level: write
      resource_type: instance

    # Adds Read and List access to all of AWS Lambda.
    - service: lambda
      access_level: read

    # Adds full access to S3 (i.e. s3:*)
    - service: s3
      access_level: all

    # You can also add multiple services at once
    - access_level: read
      service:
        - lambda
        - s3
        - iam

    # Specific resource types/ARN types can be specified too
    - access_level: all
      service: iam
      resource_type: instance-profile
    
    # ...and can be specified as a list if multiple are needed
    - access_level: all
      service: iam
      resource_type:
        - instance-profile
        - role
        - policy

    # Instead of service-wide grants, you can add specific actions...
    #

    # Adds the s3:ListBucket action permission, scoped to only
    # the given resource.
    - action: s3:ListBucket
      resource: arn:aws:s3:::my-test-bucket

    # Same as above, but with multiple resources
    - action: s3:ListBucket
      resource:
        - arn:aws:s3:::my-test-bucket
        - arn:aws:s3:::my-test-bucket/*
```

### Important: wildcard-ARN actions

Most IAM actions can be applied to a specific `Resource`. For example, `s3:PutObject` can be given `Resource: *`, or a specific object/bucket ARN. There are however some actions that cannot be constrained in this way and only make sense with `Resource: *`. For example, `ssm:DescribeParameters` and `s3:ListAllMyBuckets` can only be used with `Resource: *`, it doesn't make sense to use them with anything else.

We call these *wildcard-ARN actions*.

Due to the way the IAM database is constructed, it's impossible for `aws-iam-utils` (the library `aws-policy-generator` uses under the hood) to link wildcard-ARN actions to resource types. This means for example that if you call

```shell
aws-policy-generator --read ssm:parameter
```

Or you use the following YAML file

```yaml
policies:
  - access_level: read
    service: ssm:parameter
```

...the generated policy **will not include `ssm:DescribeParameters` by default**, even though that is clear an action related to the `ssm:parameter` resource type.

To get around this limitation, we've added a new setting. If you specify the `--include-service-wide-actions` argument (or `-S` for shorthand):

```shell
aws-policy-generator --read ssm:parameter --include-service-wide-actions
```

Or include `include_service_wide_actions` in your YAML file:

```yaml
policies:
  - access_level: read
    service: ssm:parameter
    include_service_wide_actions: true
```

Then the generated policy will include all wildcard-ARN actions for that service. This feature is turned off by default as it is non-intuitive if you are trying to craft least-privilege policies; it is typically required for specific use cases such as using the AWS console or using some Terraform resources.

In YAML you can also include a file-wide `include_service_wide_actions` setting like so:

```yaml
options:
  include_service_wide_actions: true

policies:
  - access_level: read
    service: ssm:parameter

    # inherits include_service_wide_actions from options block above
  
  - access_level: read
    service: s3:bucket

    include_service_wide_actions: false  # overrides the options block
```

This will cause all policies, unless otherwise specified, to include wildcard-ARN actions for that service.

# Licence

MIT
