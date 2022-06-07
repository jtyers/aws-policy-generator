from aws_iam_utils.constants import READ, WRITE, LIST, TAGGING, PERMISSIONS, ALL_ACCESS_LEVELS

FULL_ACCESS = '*'

ACCESS_LEVELS_MAPPINGS = {
  'list': [ LIST ],
  'read': [ LIST, READ ],
  'write': [ LIST, READ, WRITE ],
  'tagging': [ TAGGING ],
  'permissions': [ PERMISSIONS ],
  'all': FULL_ACCESS,
}
