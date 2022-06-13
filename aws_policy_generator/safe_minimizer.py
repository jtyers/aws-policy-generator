from policyuniverse.expander_minimizer import minimize_policy
from aws_iam_utils.util import lowercase_policy
from aws_iam_utils.policy import policy_from_dict

ACTION_NOT_FOUND_ERR = "Desired action not found in master permission list."

MAX_FAILS = 100


def minimize_policy_with_error_handling(policy: dict):
    """Runs minimize_policy() but ignores errors relating to unknown
    actions, removing them from the input and then re-adding afterward.
    """
    failing_actions = []
    failing_ppis = []
    policy_lowercase = policy_from_dict(lowercase_policy(policy))

    fail_counter = 0

    while True:
        fail_counter += 1
        if fail_counter == MAX_FAILS:
            raise Exception(
                f"Reached {fail_counter} errors while processing policy, "
                + "either this is too many errors or there is a bug in "
                + "aws-policy-generator"
            )

        try:
            result = minimize_policy(policy_lowercase.as_dict())
            break

        except Exception as ex:
            ex_str = str(ex)
            if not ex_str.startswith(ACTION_NOT_FOUND_ERR):
                raise ex

            failing_action = ex_str[len(ACTION_NOT_FOUND_ERR) + 1 :]
            failing_actions.append(failing_action)

        # capture the PolicyPermissionItems where failing actions appear, so
        # we also capture condition, resource, etc
        for failing_action in failing_actions:
            for ppi in policy_lowercase.ppis:
                if ppi.action == failing_action:
                    failing_ppis.append(ppi)
                    policy_lowercase.ppis.remove(ppi)
                    break

    result_policy = policy_from_dict(result)
    result_policy.ppis.extend(failing_ppis)

    return result_policy.as_dict()
