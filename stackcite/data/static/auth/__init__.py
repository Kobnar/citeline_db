from stackcite.data.static import utils


GROUP_CHOICES = utils.load_data('auth/groups.json')

GROUPS = [k for k, v in GROUP_CHOICES]

USERS, STAFF, ADMIN = GROUPS
