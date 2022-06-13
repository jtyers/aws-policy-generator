import json

from aws_policy_generator.safe_minimizer import minimize_policy_with_error_handling

# auto-shorten: tuple of (minimize, compact)
AUTO_SHORTEN_ATTEMPT = [
    (False, False),
    (True, False),
    (True, True),
]


def auto_shorten_policy(
    policy: dict, minimize: bool = False, compact: bool = False, max_length: int = 6144
) -> str:
    auto_shorten_attempts = AUTO_SHORTEN_ATTEMPT
    current_minimize = minimize
    current_compact = compact

    while True:
        if current_compact:
            policy_str = json.dumps(policy)
        else:
            policy_str = json.dumps(policy, indent=2)

        if current_minimize:
            policy_str = json.dumps(minimize_policy_with_error_handling(policy))

        policy_length = len(policy_str)
        if policy_length > max_length:
            if len(auto_shorten_attempts) == 0:
                raise ValueError(
                    f"the generated policy is {policy_length} characters, which is"
                    + " larger than the maximum {max_length} characters allowed. this"
                    + " policy is too long even after auto-shortening. try specifying"
                    + " fewer arguments"
                )

            current_minimize, current_compact = auto_shorten_attempts.pop(0)
            # loop again with new current_* args

        else:
            break

    if policy_length > max_length:
        raise ValueError(
            f"the generated policy is {policy_length} characters, which is larger than"
            + " the maximum {max_length} characters allowed. try using --compact,"
            + " --minimize, or specifying fewer arguments"
        )

    return policy_str
