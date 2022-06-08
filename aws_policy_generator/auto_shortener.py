import json

from policyuniverse.expander_minimizer import minimize_policy

# auto-shorten: tuple of (minimize, compact)
AUTO_SHORTEN_ATTEMPT = [
    (False, False),
    (True, False),
    (True, True),
]

def auto_shorten_policy(policy: dict, minimize: bool = False, compact: bool = False, max_length: int = 6144) -> str:
  auto_shorten_attempts = AUTO_SHORTEN_ATTEMPT
  current_minimize = minimize
  current_compact = compact

  while True:
      if current_compact:
          policy = json.dumps(policy)
      
      if current_minimize:
          policy = json.dumps(minimize_policy(json.loads(policy)))

      policy_length = len(policy)
      if policy_length > max_length:
          if auto_shorten:
              if len(auto_shorten_attempts) == 0:
                  raise ValueError(f"the generated policy is {policy_length} characters, which is larger than the maximum {max_length} characters allowed. this policy is too long even after auto-shortening. try specifying fewer arguments")

              current_minimize, current_compact = auto_shorten_attempts.pop(0)
              # loop again with new current_* args

          else:
              raise ValueError(f"the generated policy is {policy_length} characters, which is larger than the maximum {max_length} characters allowed. try using --compact, --minimize, or specifying fewer arguments")

      else:
          break

  if policy_length > max_length:
      raise ValueError(f"the generated policy is {policy_length} characters, which is larger than the maximum {max_length} characters allowed. try using --compact, --minimize, or specifying fewer arguments")

  return policy

