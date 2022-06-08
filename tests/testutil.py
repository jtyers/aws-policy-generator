from argparse import Namespace

FULL_ACCESS = '*'

def namespace(
    list=None,
    read=None,
    write=None,
    full_access=None,
    max_length=6144,
    auto_shorten=False,
    minimize=False,
    compact=False,
    action=None,
    file=None,
):
    return Namespace(
        list=list,
        read=read,
        write=write,
        full_access=full_access,
        max_length=max_length,
        auto_shorten=auto_shorten,
        minimize=minimize,
        compact=compact,
        action=action,
        file=file,
    )

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

