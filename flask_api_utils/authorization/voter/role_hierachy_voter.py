from flask_api_utils.authorization.voter.role_voter import RoleVoter


class RoleHierarchyVoter(RoleVoter):
    def __init__(self, hierarchy):
        self.role_hierarchy = hierarchy

    def extract_roles(self, user):
        return self.role_hierarchy.get_reachable_role_names(self.get_user_roles(user))

    def get_user_roles(self, user):
        return user.roles
